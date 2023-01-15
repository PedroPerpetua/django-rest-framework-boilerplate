"""
Stub file for restframework-simplejwt module, that does not include stubs. We type these models because mypy will
complain about missing stubs.
"""
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models


class OutstandingToken(models.Model):
    id: int
    user: AbstractUser
    jti: str
    token: str
    created_at: datetime
    expires_at: datetime
    class Meta:
            abstract: bool
            ordering: tuple[str]

class BlacklistedToken(models.Model):
    id: int
    token: OutstandingToken
    blacklisted_at: datetime
    class Meta:
        abstract: bool
