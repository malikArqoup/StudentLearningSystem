from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default="user")
    is_verified = models.BooleanField(default=False)
    institution_id = models.IntegerField(null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    locale = models.CharField(max_length=20, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []