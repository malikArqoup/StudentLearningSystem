from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default="user")
    student_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )
    is_verified = models.BooleanField(default=False)
    institution_id = models.IntegerField(null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    locale = models.CharField(max_length=20, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
