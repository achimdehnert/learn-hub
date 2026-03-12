"""Health check views (ADR-140)."""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


@csrf_exempt
@require_GET
def livez(request):
    """Liveness probe — always 200."""
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_GET
def healthz(request):
    """Readiness probe — checks DB connectivity."""
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "db": "connected"})
    except Exception as e:
        return JsonResponse({"status": "error", "db": str(e)}, status=503)
