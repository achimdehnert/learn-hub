"""Core URLs — health endpoints."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("livez/", views.livez, name="livez"),
    path("healthz/", views.healthz, name="healthz"),
]
