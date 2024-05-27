from django.db import models
from core.utility import getId
from AuthApp.models import Department,Unit
from datetime import datetime
from AuthApp.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

MANUAL_TYPE_CHOICE = [
    ("MANUALS","MANUALS"),
    ("REFERENCE BOOK","REFERENCE BOOK"),
    ("TENDER DOCUMENT","TENDER DOCUMENT"),
    ("CATALOUGE","CATALOUGE"),
    ("TECHNICAL CALCULATION","TECHNICAL CALCULATION"),
    ("TECHNICAL SPECIFICATION","TECHNICAL SPECIFICATION"),
    ("TECHNICAL REPORT","TECHNICAL REPORT"),
    ("PROJECT REPORT","PROJECT REPORT"),
]

MANUAL_LOG_STATUS_CHOICE = [
    ("View Document", "VIEW"),
    ("Add Document", "ADD"),
    ("Update Document", "UPDATE"),
    ("Archive Document", "ARCHIVE"),
    ("Delete Document", "DELETE"),
]



class Manual(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    manual_type = models.CharField(max_length=100, choices=MANUAL_TYPE_CHOICE, default=MANUAL_TYPE_CHOICE[0][0])
    manual_no = models.CharField(max_length=100, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    supplier = models.CharField(max_length=250, null=True)
    package_no = models.CharField(max_length=100, null=True) # manuals
    letter_no = models.CharField(max_length=100, null=True)
    registration_date = models.CharField(max_length=10,null=True)
    description = models.TextField(null=True)
    remarks = models.TextField(null=True)
    upload_file = models.FileField(upload_to="manual/", null=True) # all model
    editor = models.CharField(max_length=100, null=True)
    source = models.CharField(max_length=100, null=True)
    author = models.CharField(max_length=100, null= True) # reference book
    capacity = models.CharField(max_length=100, null=True)
    year = models.CharField(max_length=10, null=True)  # project report
    is_archive = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    archive_reason = models.TextField(null = True)
   
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('man_')
            while Manual.objects.filter(id = self.id).exists():
                self.id = getId('man_')
        super(Manual, self).save()
        
        
class ManualLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manual = models.ForeignKey(Manual, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=MANUAL_LOG_STATUS_CHOICE, default=MANUAL_LOG_STATUS_CHOICE[0][0])
    message = models.CharField(max_length=255)
    details = models.TextField()
    action_time = models.DateTimeField(default=datetime.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("mnl")
            while ManualLog.objects.filter(id=self.id).exists():
                self.id = getId("mnl")
        super(ManualLog, self).save()
        
        
@receiver(post_delete, sender=Manual)
def manual_model_post_delete(sender, instance, **kwargs):
    try:
        if instance.upload_file:
            file_path = instance.upload_file.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        else:
            print("Failed to Delete Manual attachment.")
    except Exception as e:
        print(f"Error deleting files: {e}")