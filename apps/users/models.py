from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        SPONSOR = "sponsor", "Sponsor"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
