"""Platform-wide smoke tests — verify ALL domains and key endpoints are reachable.

Tests every production domain via real HTTPS requests. No Django DB required.
Run with: pytest tests/test_smoke_all_domains.py -v --timeout=30

Requires: requests (pip install requests)
"""

import pytest
import requests

# ---------------------------------------------------------------------------
# Timeout for all HTTP requests (seconds)
# ---------------------------------------------------------------------------
TIMEOUT = 15

# ---------------------------------------------------------------------------
# Platform Domain Registry
#
# Format: (domain, expected_status, description)
#   expected_status: HTTP status code or tuple of acceptable codes
# ---------------------------------------------------------------------------

PLATFORM_APPS = {
    # ── Coach Hub (kiohnerisiko.de) ──────────────────────────────────
    "coach-hub": {
        "domain": "kiohnerisiko.de",
        "port": 8007,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", 200),
            ("/livez/", 200),
            ("/readyz/", 200),
            ("/admin/login/", 200),
        ],
    },
    "coach-hub-staging": {
        "domain": "staging.kiohnerisiko.de",
        "port": 8017,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", 200),
        ],
    },
    # ── Learn Hub (learn.iil.pet) ────────────────────────────────────
    "learn-hub": {
        "domain": "learn.iil.pet",
        "port": 8100,
        "endpoints": [
            ("/", 200),
            ("/healthz/", 200),
            ("/livez/", 200),
            ("/readyz/", 200),
            ("/kurse/", 200),
            ("/api/", (200, 401, 403)),
            ("/admin/login/", (200, 301, 302)),
        ],
    },
    # ── Billing Hub (billing.iil.pet) ────────────────────────────────
    "billing-hub": {
        "domain": "billing.iil.pet",
        "port": 8092,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", 200),
            ("/livez/", 200),
        ],
    },
    # ── Trading Hub (ai-trades.de) ───────────────────────────────────
    "trading-hub": {
        "domain": "ai-trades.de",
        "port": 8088,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", (200, 404)),
        ],
    },
    # ── CAD Hub (nl2cad.de) ──────────────────────────────────────────
    "cad-hub": {
        "domain": "nl2cad.de",
        "port": 8094,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", (200, 404)),
        ],
    },
    # ── PPTX Hub (prezimo.de / prezimo.com) ──────────────────────────
    "pptx-hub-de": {
        "domain": "prezimo.de",
        "port": 8020,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", (200, 404)),
        ],
    },
    "pptx-hub-com": {
        "domain": "prezimo.com",
        "port": None,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── Weltenhub (weltenforger.com / weltenforger.de) ───────────────
    "weltenhub-com": {
        "domain": "weltenforger.com",
        "port": 8081,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", (200, 404)),
        ],
    },
    "weltenhub-de": {
        "domain": "weltenforger.de",
        "port": None,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── Travel Beat / DriftTales ─────────────────────────────────────
    "drifttales-com": {
        "domain": "drifttales.com",
        "port": 8089,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    "drifttales-app": {
        "domain": "drifttales.app",
        "port": None,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── Wedding Hub ──────────────────────────────────────────────────
    "wedding-hub": {
        "domain": "wedding-hub.iil.pet",
        "port": 8093,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", (200, 404)),
        ],
    },
    # ── Illustration Hub ─────────────────────────────────────────────
    "illustration-hub": {
        "domain": "illustration.iil.pet",
        "port": 8096,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── Writing Hub ──────────────────────────────────────────────────
    "writing-hub": {
        "domain": "writing.iil.pet",
        "port": 8097,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── Research Hub ─────────────────────────────────────────────────
    "research-hub": {
        "domain": "dsb.iil.pet",
        "port": 8098,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── Ausschreibungs Hub ───────────────────────────────────────────
    "ausschreibungs-hub": {
        "domain": "bieterpilot.de",
        "port": 8095,
        "endpoints": [
            ("/", (200, 301, 302)),
            ("/healthz/", (200, 404)),
            ("/livez/", (200, 404)),
        ],
    },
    # ── BF Agent ─────────────────────────────────────────────────────
    "bfagent": {
        "domain": "bfagent.iil.pet",
        "port": 8091,
        "endpoints": [
            ("/", (200, 301, 302, 401, 403)),
        ],
    },
    # ── DevHub ───────────────────────────────────────────────────────
    "devhub": {
        "domain": "devhub.iil.pet",
        "port": 8085,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── Schutztat (Risk Hub) ─────────────────────────────────────────
    "risk-hub": {
        "domain": "schutztat.com",
        "port": 8082,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── iil.pet (Platform Root) ──────────────────────────────────────
    "iil-pet": {
        "domain": "iil.pet",
        "port": None,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── iil.ai ───────────────────────────────────────────────────────
    "iil-ai": {
        "domain": "iil.ai",
        "port": None,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
    # ── 137herz ──────────────────────────────────────────────────────
    "137herz": {
        "domain": "137herz.de",
        "port": None,
        "endpoints": [
            ("/", (200, 301, 302)),
        ],
    },
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _normalize_expected(expected):
    """Normalize expected status to a tuple."""
    if isinstance(expected, int):
        return (expected,)
    return expected


def _get(url, **kwargs):
    """GET with timeout, follow redirects disabled."""
    return requests.get(
        url, timeout=TIMEOUT, allow_redirects=False,
        headers={"User-Agent": "bf-platform-smoke/1.0"}, **kwargs,
    )


# ---------------------------------------------------------------------------
# Test parameter generation
# ---------------------------------------------------------------------------

def _generate_external_params():
    """Generate (app_name, domain, path, expected) tuples for external tests."""
    params = []
    for app_name, cfg in PLATFORM_APPS.items():
        domain = cfg["domain"]
        for path, expected in cfg["endpoints"]:
            test_id = f"{app_name}:{domain}{path}"
            params.append(
                pytest.param(domain, path, expected, id=test_id)
            )
    return params


def _generate_internal_params():
    """Generate (app_name, port, path, expected) tuples for internal tests."""
    params = []
    for app_name, cfg in PLATFORM_APPS.items():
        port = cfg.get("port")
        if port is None:
            continue
        for path, expected in cfg["endpoints"]:
            test_id = f"{app_name}:localhost:{port}{path}"
            params.append(
                pytest.param(port, path, expected, id=test_id)
            )
    return params


# ---------------------------------------------------------------------------
# Tests — External (via Cloudflare Tunnel / public HTTPS)
# ---------------------------------------------------------------------------

class TestExternalSmoke:
    """Smoke tests via public HTTPS — tests Cloudflare + Nginx + App."""

    @pytest.mark.parametrize("domain,path,expected", _generate_external_params())
    def test_endpoint_reachable(self, domain, path, expected):
        """Every registered endpoint must return an acceptable status."""
        url = f"https://{domain}{path}"
        expected = _normalize_expected(expected)
        try:
            resp = _get(url)
        except requests.ConnectionError:
            pytest.fail(f"CONNECTION REFUSED: {url}")
        except requests.Timeout:
            pytest.fail(f"TIMEOUT ({TIMEOUT}s): {url}")

        assert resp.status_code in expected, (
            f"GET {url} → {resp.status_code} (expected {expected})"
        )


# ---------------------------------------------------------------------------
# Tests — Internal (via localhost ports, run ON the server)
# ---------------------------------------------------------------------------

class TestInternalSmoke:
    """Smoke tests via localhost — tests App directly (skip Nginx/CF).

    Run these on the production server:
        ssh root@88.198.191.108
        pytest tests/test_smoke_all_domains.py -k internal -v
    """

    @pytest.mark.parametrize("port,path,expected", _generate_internal_params())
    def test_endpoint_reachable(self, port, path, expected):
        """Every app port must respond on localhost."""
        url = f"http://127.0.0.1:{port}{path}"
        expected = _normalize_expected(expected)
        try:
            resp = _get(url)
        except requests.ConnectionError:
            pytest.fail(f"CONNECTION REFUSED: {url} — container down?")
        except requests.Timeout:
            pytest.fail(f"TIMEOUT ({TIMEOUT}s): {url}")

        assert resp.status_code in expected, (
            f"GET {url} → {resp.status_code} (expected {expected})"
        )


# ---------------------------------------------------------------------------
# Tests — DNS / TLS
# ---------------------------------------------------------------------------

class TestDNSAndTLS:
    """Verify DNS resolution and TLS certificate validity for all domains."""

    ALL_DOMAINS = sorted({cfg["domain"] for cfg in PLATFORM_APPS.values()})

    @pytest.mark.parametrize("domain", ALL_DOMAINS)
    def test_dns_resolves(self, domain):
        """Every domain must resolve in DNS."""
        import socket
        try:
            socket.getaddrinfo(domain, 443)
        except socket.gaierror:
            pytest.fail(f"DNS resolution failed for {domain}")

    @pytest.mark.parametrize("domain", ALL_DOMAINS)
    def test_tls_valid(self, domain):
        """Every domain must have a valid TLS certificate."""
        import ssl
        import socket
        ctx = ssl.create_default_context()
        try:
            with socket.create_connection((domain, 443), timeout=TIMEOUT) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    assert cert is not None, f"No TLS cert for {domain}"
        except ssl.SSLCertVerificationError as e:
            pytest.fail(f"TLS cert invalid for {domain}: {e}")
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            pytest.fail(f"Cannot connect to {domain}:443 — {e}")


# ---------------------------------------------------------------------------
# Summary — run standalone
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("BF Platform — Domain Smoke Test Summary")
    print("=" * 70)

    total = 0
    ok = 0
    fail = 0

    for app_name, cfg in sorted(PLATFORM_APPS.items()):
        domain = cfg["domain"]
        for path, expected in cfg["endpoints"]:
            url = f"https://{domain}{path}"
            expected = _normalize_expected(expected)
            total += 1
            try:
                resp = _get(url)
                status = resp.status_code
                passed = status in expected
            except Exception as e:
                status = f"ERR: {e.__class__.__name__}"
                passed = False

            icon = "OK" if passed else "FAIL"
            if passed:
                ok += 1
            else:
                fail += 1
            print(f"  [{icon:4s}] {app_name:25s} {url:55s} → {status}")

    print("-" * 70)
    print(f"  Total: {total}  |  OK: {ok}  |  FAIL: {fail}")
    print("=" * 70)
