"""Shared pytest fixtures for django-ai-boost tests."""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path

import django
import pytest
from asgiref.sync import sync_to_async
from django.apps import apps

PROJECT_ROOT = Path(__file__).parent
TESTPROJECT_PATH = PROJECT_ROOT / "fixtures" / "testproject"


@pytest.fixture(scope="session", autouse=True)
def django_setup() -> None:
    """Configure and initialize Django once for the whole test session."""
    if str(TESTPROJECT_PATH) not in sys.path:
        sys.path.insert(0, str(TESTPROJECT_PATH))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")

    if not apps.ready:
        django.setup()


@pytest.fixture
def async_django_db(django_setup: None) -> Callable[..., Callable[..., object]]:
    """Return sync_to_async to wrap ORM calls inside async tests."""
    return sync_to_async


@pytest.fixture
def flush_root_handlers() -> Callable[[], None]:
    """Flush root logger handlers so file logs are written before assertions."""

    def _flush() -> None:
        for handler in logging.getLogger().handlers:
            flush = getattr(handler, "flush", None)
            if callable(flush):
                flush()

    return _flush
