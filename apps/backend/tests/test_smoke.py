"""Smoke test for the Python workspace itself.

Once the Django project exists, this is replaced by real domain tests — its only job
right now is to prove that uv, pytest, and coverage are wired correctly end to end.
"""

import chronos_backend


def test_chronos_backend_package_imports() -> None:
    assert chronos_backend is not None
