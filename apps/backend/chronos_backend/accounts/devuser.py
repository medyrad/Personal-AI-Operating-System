"""Single shared source for the placeholder dev user.

Every API module calls this instead of defining its own get-or-create — see the auth
note in chronos_backend/events/api.py for why there's no real auth yet.
"""

from .models import User


def get_dev_user() -> User:
    user, _ = User.objects.get_or_create(
        username="dev",
        defaults={"timezone": "Europe/Berlin", "wake_time_default": "07:00"},
    )
    return user
