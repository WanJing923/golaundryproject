from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email_address = models.EmailField(unique=True, default="example@example.com")
    firebase_uid = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username