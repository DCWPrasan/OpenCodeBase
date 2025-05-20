from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from AdminApp.utils import getId
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from .modelManager import CustomUserManager


USER_TYPE_CHOICES = [("Admin", "ADMIN"), ("User", "User")]


def user_permission():
    return {
        "manage_rack": False,
        "manage_material": False,
        "manage_barcode": False,
        "view_report": False,
        "view_demand_forecast": False,
        "view_analysis": False,
        "manage_stockin": False,
        "manage_stockout": False,
        "consumption_stockout": False
    }

PERMISSION_KEYS=user_permission().keys()


class Designation(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=235, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("des_")
            while Designation.objects.filter(id=self.id).exists():
                self.id = getId("des_")
        super(Designation, self).save()


class Users(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    role = models.CharField(
        default=USER_TYPE_CHOICES[0][0], choices=USER_TYPE_CHOICES, max_length=10
    )
    personnel_number = models.CharField(unique=True, max_length=16, db_index=True)
    email = models.EmailField(_("email address"), unique=True, null=True)
    name = models.CharField(max_length=50, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    secret_token = models.TextField()
    mobile_number = models.CharField(max_length=10, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)
    user_permission = models.JSONField(default=user_permission)
    is_allow_email_daily_report = models.BooleanField(default=False)
    is_allow_email_low_stock_alert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "personnel_number"
    REQUIRED_FIELDS = ["name", "email"]
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("usr_")
            while Users.objects.filter(id=self.id).exists():
                self.id = getId("usr_")
        super(Users, self).save()


class LogInOutLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    details = models.TextField()
    device_info = models.TextField(null=True)
    action_time = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("lio")
            while LogInOutLog.objects.filter(id=self.id).exists():
                self.id = getId("lio")
        super(LogInOutLog, self).save()
