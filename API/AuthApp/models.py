from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid

USER_ROLE_CHOICES = [
    ('SuperAdmin', "SUPERADMIN"),
    ('Admin', "ADMIN"),
    ('User', "USER")
]

def default_drawing_permission():
    return {"ps": False, "fdr": False, "misc": False, "disable_dwg_file":True, "download_drawing":False, "view_layout":False}

def default_standard_permission():
    return {"awwa": False, "astm": False, "api": False, "british":False, "din_german":False, "gost_russian":False, "iec":False, "iso":False, "irst":False, "psn":False, "other_standard":False}

def default_document_permission():
    return {"reference_book": False, "tender_document": False, "catalouge": False,"technical_calculation": False, "technical_specification": False, "technical_report": False,"project_report": False, "project_submitted_drawings": False}

def getId(prefix: str = "") -> str:
    return f'{prefix}{uuid.uuid4().hex}'

class Department(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=250, unique=True)
    department_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("dep_")
            while Department.objects.filter(id=self.id).exists():
                self.id = getId("dep_")
        super(Department, self).save()

class OldDepartment(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    new_department = models.OneToOneField(Department, on_delete=models.CASCADE, db_index=True)
    old_names = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("odp_")
            while OldDepartment.objects.filter(id=self.id).exists():
                self.id = getId("odp_")
        super(OldDepartment, self).save()

class Unit(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=250, unique=True)
    unit_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("uni_")
            while Unit.objects.filter(id=self.id).exists():
                self.id = getId("uni_")
        super(Unit, self).save()

class Volume(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    volume_id = models.IntegerField()
    name = models.CharField(max_length=300)

    def save(self, *args, **kwargs):
        if not self.volume_id:
            self.volume_id = Volume.objects.all().count()
            while Volume.objects.filter(volume_id=self.volume_id).exists():
                self.volume_id = Volume.objects.all().count() + 1

        if not self.id:
            self.id = getId("vol_")
            while Volume.objects.filter(id=self.id).exists():
                self.id = getId("vol_")
        super(Volume, self).save()

class Subvolume(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=300)
    sub_volume_no = models.CharField(max_length=10)
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("svl_")
            while Subvolume.objects.filter(id=self.id).exists():
                self.id = getId("svl_")
        super(Subvolume, self).save()


class CustomUserManager(BaseUserManager):
    def create_user(self, personnel_number, full_name, email, phone_number, designation, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(personnel_number=personnel_number, full_name=full_name, email=email, phone_number=phone_number, designation=designation, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, personnel_number, full_name, email, phone_number, designation, password):
        user = self.create_user(personnel_number, full_name, email, phone_number, designation, password=password, role="SuperAdmin")
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    profile_photo = models.ImageField(upload_to="profile_photo/", null=True) # all model
    personnel_number = models.CharField(unique=True, max_length=200)
    full_name = models.CharField(max_length=50)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    role = models.CharField(default=USER_ROLE_CHOICES[0][0], choices=USER_ROLE_CHOICES, max_length=10)
    designation = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    jti_token = models.CharField(max_length=50, null=True, unique = True)  # Store session token
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    drawing_permission = models.JSONField(default=default_drawing_permission)
    standard_permission = models.JSONField(default=default_standard_permission)
    document_permission = models.JSONField(default=default_document_permission)
    last_login = models.DateTimeField(null=True)
    last_logout = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'personnel_number'
    REQUIRED_FIELDS = ["full_name", "email", "phone_number", "designation"]
    objects = CustomUserManager()

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('usr_')
            while User.objects.filter(id=self.id).exists():
                self.id = getId('usr_')
        super(User, self).save()


class LogInOutLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    details = models.TextField()
    device_info = models.TextField(null = True)
    action_time = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("lio")
            while LogInOutLog.objects.filter(id=self.id).exists():
                self.id = getId("lio")
        super(LogInOutLog, self).save()
