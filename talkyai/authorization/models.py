from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='authorization_user_set',  # Add a unique related name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='authorization_user_set',  # Add a unique related name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
