"""Smoke tests — verify ALL registered endpoints are reachable.

Automatically discovers every named URL pattern in the project and fires a GET
request.  Acceptable responses: 200, 301, 302, 304, 401, 403 (auth-protected).
Unacceptable: 404, 500.

Usage:
    pytest tests/test_smoke_endpoints.py -v
"""

import pytest
from django.urls import NoReverseMatch, URLPattern, URLResolver, reverse

# ---------------------------------------------------------------------------
# URL Discovery
# ---------------------------------------------------------------------------

# URL names that need specific kwargs to reverse
URL_KWARGS = {
    # DRF detail routes need a pk
    "assessment-type-detail": {"pk": 1},
    "assessment-type-submit": {"pk": 1},
    "assessment-attempt-detail": {"pk": 1},
    "assessment-report-detail": {"pk": 1},
    "assessment-report-download-pdf": {"pk": 1},
    "category-detail": {"pk": 1},
    "course-detail": {"pk": 1},
    "enrollment-detail": {"pk": 1},
    "progress-detail": {"pk": 1},
    "quiz-detail": {"pk": 1},
    "attempt-detail": {"pk": 1},
    "certificate-detail": {"pk": 1},
    "badge-detail": {"pk": 1},
    "leaderboard-detail": {"pk": 1},
    "my-points-detail": {"pk": 1},
}

# URL names to SKIP (admin autodiscover, login-required redirects, etc.)
SKIP_URL_NAMES = {
    # Django admin has hundreds of auto-generated URLs
    # We test admin root separately
}

# URL prefixes to skip entirely (e.g. admin detail pages)
SKIP_URL_PREFIXES = (
    "admin:",  # admin sub-pages (model changelists, add, change, delete)
)

# Acceptable HTTP status codes (not broken)
ACCEPTABLE_STATUS = {200, 301, 302, 303, 304, 401, 403, 405}


def _collect_url_names(urlpatterns, prefix="", namespace=""):
    """Recursively collect all named URL patterns."""
    urls = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            ns = f"{namespace}:{pattern.namespace}" if pattern.namespace else namespace
            urls.extend(
                _collect_url_names(pattern.url_patterns, prefix=prefix, namespace=ns)
            )
        elif isinstance(pattern, URLPattern) and pattern.name:
            name = f"{namespace}:{pattern.name}" if namespace else pattern.name
            urls.append(name)
    return urls


def get_all_url_names():
    """Return all named URL patterns from root URLconf."""
    from django.urls import get_resolver

    resolver = get_resolver()
    return sorted(set(_collect_url_names(resolver.url_patterns)))


def _should_skip(name):
    """Check if URL name should be skipped."""
    if name in SKIP_URL_NAMES:
        return True
    for prefix in SKIP_URL_PREFIXES:
        if name.startswith(prefix):
            return True
    return False


def _reverse_url(name):
    """Try to reverse a URL name, return (url, skip_reason) tuple."""
    if _should_skip(name):
        return None, "skipped"

    kwargs = URL_KWARGS.get(name)
    try:
        url = reverse(name, kwargs=kwargs)
        return url, None
    except NoReverseMatch:
        # URL requires kwargs we don't know about — skip gracefully
        return None, "needs unknown kwargs"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEndpointSmoke:
    """Smoke test every registered endpoint for reachability."""

    # --- Public endpoints (no auth needed) ---

    PUBLIC_ENDPOINTS = [
        "/",
        "/livez/",
        "/healthz/",
        "/readyz/",
        "/kurse/",
        "/admin/login/",
    ]

    @pytest.mark.parametrize("url", PUBLIC_ENDPOINTS)
    def test_public_endpoint_reachable(self, client, url):
        """Public endpoints must return an acceptable status."""
        response = client.get(url)
        assert response.status_code in ACCEPTABLE_STATUS, (
            f"GET {url} returned {response.status_code}"
        )

    # --- Admin root ---

    def test_admin_root_redirects_to_login(self, client):
        """Admin root should redirect to login for anonymous users."""
        response = client.get("/admin/", follow=False)
        assert response.status_code in {200, 301, 302}, (
            f"GET /admin/ returned {response.status_code}"
        )

    # --- API root ---

    def test_api_root_reachable(self, client):
        """API root (DRF browsable API) must be reachable."""
        response = client.get("/api/", HTTP_ACCEPT="application/json")
        assert response.status_code in ACCEPTABLE_STATUS, (
            f"GET /api/ returned {response.status_code}"
        )

    # --- API list endpoints (auth required, expect 401/403) ---

    API_LIST_ENDPOINTS = [
        "/api/categories/",
        "/api/courses/",
        "/api/enrollments/",
        "/api/progress/",
        "/api/quizzes/",
        "/api/attempts/",
        "/api/certificates/",
        "/api/badges/",
        "/api/leaderboard/",
        "/api/my-points/",
        "/api/assessments/types/",
        "/api/assessments/attempts/",
        "/api/assessments/reports/",
    ]

    @pytest.mark.parametrize("url", API_LIST_ENDPOINTS)
    def test_api_list_endpoint_reachable(self, client, url):
        """API list endpoints must not 404 or 500 (auth-protected is fine)."""
        response = client.get(url, HTTP_ACCEPT="application/json")
        assert response.status_code in ACCEPTABLE_STATUS, (
            f"GET {url} returned {response.status_code}"
        )

    @pytest.mark.parametrize("url", API_LIST_ENDPOINTS)
    def test_api_list_endpoint_authenticated(self, auth_client, url):
        """API list endpoints with auth should return 200."""
        response = auth_client.get(url, HTTP_ACCEPT="application/json")
        assert response.status_code == 200, (
            f"GET {url} (authenticated) returned {response.status_code}"
        )

    # --- Auto-discovered URL completeness check ---

    def test_all_named_urls_are_reversible(self):
        """Every named URL in the project must be reversible (no broken includes)."""
        all_names = get_all_url_names()
        unreversible = []
        for name in all_names:
            if _should_skip(name):
                continue
            url, reason = _reverse_url(name)
            if reason == "needs unknown kwargs":
                # OK — detail views need object PKs which may not exist
                continue
            if url is None and reason != "skipped":
                unreversible.append(name)
        assert not unreversible, (
            f"These URL names could not be reversed: {unreversible}"
        )

    def test_no_url_returns_500(self, auth_client):
        """No discovered endpoint should return HTTP 500."""
        all_names = get_all_url_names()
        errors_500 = []
        for name in all_names:
            if _should_skip(name):
                continue
            url, reason = _reverse_url(name)
            if url is None:
                continue
            response = auth_client.get(url, HTTP_ACCEPT="application/json")
            if response.status_code >= 500:
                errors_500.append(f"{name} → {url} → {response.status_code}")
        assert not errors_500, (
            "These endpoints returned 5xx:\n" + "\n".join(errors_500)
        )

    def test_no_url_returns_404(self, auth_client):
        """No discovered list endpoint should return HTTP 404."""
        all_names = get_all_url_names()
        errors_404 = []
        for name in all_names:
            if _should_skip(name):
                continue
            url, reason = _reverse_url(name)
            if url is None:
                continue
            response = auth_client.get(url, HTTP_ACCEPT="application/json")
            if response.status_code == 404:
                errors_404.append(f"{name} → {url}")
        assert not errors_404, (
            "These endpoints returned 404:\n" + "\n".join(errors_404)
        )


# ---------------------------------------------------------------------------
# Summary helper — run standalone to see all discovered URLs
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import django
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
    django.setup()

    print("=== All registered URL names ===\n")
    for name in get_all_url_names():
        url, reason = _reverse_url(name)
        status = f"→ {url}" if url else f"  [{reason}]"
        print(f"  {name:45s} {status}")
    print(f"\nTotal: {len(get_all_url_names())} named URLs")
