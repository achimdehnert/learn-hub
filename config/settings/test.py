"""Learn Hub — Test Settings (ADR-141: PostgreSQL-Only Testing)"""
import os

from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Override decouple secrets with test defaults
SECRET_KEY = "test-secret-key-not-for-production"

# ADR-141: Explicit PostgreSQL — SQLite is BANNED for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("TEST_DB_NAME", "learn_hub_test"),
        "USER": os.environ.get("TEST_DB_USER", "dehnert"),
        "PASSWORD": os.environ.get("TEST_DB_PASSWORD", ""),
        "HOST": os.environ.get("TEST_DB_HOST", "localhost"),
        "PORT": os.environ.get("TEST_DB_PORT", "5434"),
        "TEST": {"NAME": "test_learn_hub"},
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

SILENCED_SYSTEM_CHECKS = [
    "security.W004",
    "security.W008",
    "security.W009",
    "security.W012",
    "security.W016",
    "iil_learnfw.W001",  # IP hash salt not needed in tests
    "iil_learnfw.W002",  # Lead capture email backend not needed in tests
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "root": {"handlers": ["null"], "level": "CRITICAL"},
}
