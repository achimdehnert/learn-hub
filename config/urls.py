"""URL configuration for learn-hub."""

from django.contrib import admin
from django.urls import include, path

from config.healthz import liveness, readiness

urlpatterns = [
    path("livez/", liveness, name="livez"),
    path("healthz/", readiness, name="healthz"),
    path("readyz/", readiness, name="readyz"),
    path("admin/", admin.site.urls),
    path("kurse/", include("iil_learnfw.urls")),
    path("", include("apps.core.urls")),
]
