from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from AdminApp.utils import getId
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from .modelManager import CustomUserManager


USER_TYPE_CHOICES = [
    ('SuperAdmin', "SUPERADMIN"), ('Admin', "ADMIN"), ('Employee', "EMPLOYEE")
]

class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    role = models.CharField(default=USER_TYPE_CHOICES[0][0],choices=USER_TYPE_CHOICES,max_length=10)
    personnel_number = models.CharField(unique=True, max_length=200)
    name = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'personnel_number'
    REQUIRED_FIELDS = ['name']
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('usr_')
            while User.objects.filter(id=self.id).exists():
                self.id = getId('usr_')
        super(User, self).save()

