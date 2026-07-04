"""Custom User model.

Set as AUTH_USER_MODEL from the very first migration (see docs/data-model.md, section
`User`) — switching this later requires a painful data migration, so we pay the small
extra cost now instead.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    timezone = models.CharField(
        max_length=64,
        default="UTC",
        help_text="IANA timezone name, e.g. 'Europe/Berlin'. Used by the Planner Agent.",
    )
    wake_time_default = models.TimeField(null=True, blank=True)
    sleep_time_default = models.TimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.username
