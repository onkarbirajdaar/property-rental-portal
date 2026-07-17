from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    ROLE_CHOICES = [
        ("tenant", "Tenant"),
        ("owner", "Owner"),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="tenant"
    )
    photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username} Profile"
