from django.db import models
from django.utils.translation import gettext_lazy as _
from AuthApp.utils import getId
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from .modelManager import CustomUserManager
from django.core.exceptions import ValidationError

USER_ROLE_CHOICES = [
    ("Admin", 'Admin'),
    ("Executive", 'Executive'),
    ("Area Incharge", 'Area Incharge'),
    ("Shift Incharge", 'Shift Incharge'),
]

AREA_LIST = [
    "Weighing Maintenance", 
    "Weighing Operation", 
    "Repair Labs", 
    "Power Labs", 
    "Automation",
    "CCTV",
]

def default_area():
    return {"name":[]}

class User(AbstractBaseUser):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    role = models.CharField(default=USER_ROLE_CHOICES[0][0], choices=USER_ROLE_CHOICES, max_length=15)
    personnel_number = models.CharField(unique=True, max_length=200)
    name = models.CharField(max_length=50, db_index=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    area = models.JSONField(default=default_area)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "personnel_number"
    REQUIRED_FIELDS = ["name"]
    objects = CustomUserManager()

    def clean(self):
        super().clean()
        if self.role in ["Area Incharge", "Shift Incharge"] and not self.area:
            raise ValidationError({
                'area': 'Area is required for Area Incharge and Shift Incharge roles'
            })
        if self.role in ["Admin", "Executive"] and self.area:
            self.area = default_area()  # Reset area to default if not required

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("usr_")
            while User.objects.filter(id=self.id).exists():
                self.id = getId("usr_")
        self.full_clean()  # This will call clean() method for validation
        super(User, self).save(*args, **kwargs)

class LogInOutLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
        super(LogInOutLog, self).save(*args, **kwargs)