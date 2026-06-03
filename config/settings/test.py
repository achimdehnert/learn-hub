"""Learn Hub — Test Settings (ADR-179: PostgreSQL-Only Testing)"""

import os

from decouple import config

# base.py reads SECRET_KEY = config("DJANGO_SECRET_KEY") at IMPORT time with no
# default (intentional prod fail-loud guard). In CI/test there is no real secret,
# so seed a throwaway value BEFORE importing base — otherwise the import below
# crashes with UndefinedValueError before our SECRET_KEY override can apply.
# Prod is unaffected: it sets DJANGO_SECRET_KEY, so setdefault is a no-op there.
os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key-not-for-production")

from .base import *  # noqa: E402, F401, F403

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Override decouple secrets with test defaults
SECRET_KEY = "test-secret-key-not-for-production"  # hardcoded-ok: test settings
# ADR-179: Explicit PostgreSQL — SQLite is BANNED for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        # Platform-CI convention is POSTGRES_* on localhost:5432 (test_user/test_pass/
        # test_db); shared _ci-python.yml sets POSTGRES_HOST and runs the service there.
        # Fall back to the older TEST_DB_* local-dev vars so existing .env setups keep
        # working; final defaults match the CI postgres service.
        "NAME": config("POSTGRES_DB", default=config("TEST_DB_NAME", default="test_db")),
        "USER": config("POSTGRES_USER", default=config("TEST_DB_USER", default="test_user")),
        "PASSWORD": config(
            "POSTGRES_PASSWORD", default=config("TEST_DB_PASSWORD", default="test_pass")
        ),
        "HOST": config("POSTGRES_HOST", default=config("TEST_DB_HOST", default="localhost")),
        "PORT": config("POSTGRES_PORT", default=config("TEST_DB_PORT", default="5432")),
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
