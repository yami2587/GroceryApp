from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_manager = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    def save(self, *args, **kwargs):

        if self.is_manager:
            self.is_customer = True
        super().save(*args, **kwargs)
