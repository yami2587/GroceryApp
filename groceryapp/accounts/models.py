from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('manager', 'Manager'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.role})"
    
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    house_no = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    default = models.BooleanField(default=False)
    country = models.CharField(max_length=100, default='India')

    def __str__(self):
        return f"{self.full_name}, {self.house_no}, {self.city}"
