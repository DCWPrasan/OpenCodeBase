from django.db import models

# Create your models here.
from core.utility import getId
from AuthApp.models import User
from datetime import datetime
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os



STANDARD_TYPE_CHOICE = [
    ("BIS","BIS"),
    ("ASTM","ASTM"),
    ("AWWA","AWWA"),
    ("BRITISH","BRITISH"),
    ("DIN(GERMAN)","DIN(GERMAN)"),
    ("GOST(RUSSIAN)","GOST(RUSSIAN)"),
    ("IEC","IEC"),
    ("ISO","ISO"),
    ("IRST","IRST"),
    ("API","API"),
    ("PSN","PSN"),
    ("RSN","RSN"),
    ("IPSS","IPSS")
]

STANDARD_LOG_STATUS_CHOICE = [
    ("View Standard", "VIEW"),
    ("Add Standard", "ADD"),
    ("Update Standard", "UPDATE"),
    ("Archive Standard", "ARCHIVE"),
    ("Delete Standard", "DELETE"),
]



class RSNVolume(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    volume_no = models.CharField(max_length=100)
    volume_title = models.CharField(max_length=250)
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('rsv_')
            while RSNVolume.objects.filter(id=self.id).exists():
                self.id = getId('rsv_')
        super(RSNVolume, self).save()


class RSNGroup(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    name = models.CharField(max_length=500, null=True)
    group_id = models.CharField(max_length=255)
    rsn_volume = models.ForeignKey(RSNVolume, on_delete=models.CASCADE, null=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('rsg_')
            while RSNGroup.objects.filter(id=self.id).exists():
                self.id = getId('rsg_')
        super(RSNGroup, self).save()
    

class IPSSTitle(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    title_id = models.CharField(max_length=5)
    title = models.CharField(max_length=250)
    
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('ipt_')
            while IPSSTitle.objects.filter(id=self.id).exists():
                self.id = getId('ipt_')
        super(IPSSTitle, self).save()
    
    
    
class Standard(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    standard_type = models.CharField(max_length=100, choices=STANDARD_TYPE_CHOICE, default=STANDARD_TYPE_CHOICE[5][0])
    standard_no = models.CharField(max_length=100, db_index=True)
    part_no = models.CharField(max_length=100,null=True)
    section_no = models.CharField(max_length=100,null=True)
    document_year = models.CharField(max_length=10,null=True)
    division = models.CharField(max_length=100,null=True)
    division_code = models.CharField(max_length=100,null=True)
    committee_code = models.CharField(max_length=100,null=True)
    committee_title = models.CharField(max_length=100,null=True)
    description = models.TextField(null=True)
    upload_file = models.FileField(upload_to='standard/', null=True)
    rsn_volume = models.ForeignKey(RSNVolume,on_delete=models.SET_NULL ,null=True)
    group = models.ForeignKey(RSNGroup, on_delete=models.SET_NULL, null=True)
    no_of_sheet = models.IntegerField(null=True)
    title = models.ForeignKey(IPSSTitle, on_delete=models.SET_NULL, null=True)
    file_availability = models.BooleanField(null=True)
    is_archive = models.BooleanField(default=False)
    archive_reason = models.TextField(null = True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('sta_')
            while Standard.objects.filter(id=self.id).exists():
                self.id = getId('sta_')
        super(Standard, self).save()
        
        

class StandardLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    standard = models.ForeignKey(Standard, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STANDARD_LOG_STATUS_CHOICE, default=STANDARD_LOG_STATUS_CHOICE[0][0])
    message = models.CharField(max_length=255)
    details = models.TextField()
    action_time = models.DateTimeField(default=datetime.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("sdl")
            while StandardLog.objects.filter(id=self.id).exists():
                self.id = getId("sdl")
        super(StandardLog, self).save()




# Define a signal receiver function
@receiver(post_delete, sender=Standard)
def standard_model_post_delete(sender, instance, **kwargs):
    try:
        if instance.upload_file:
            file_path = instance.upload_file.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        else:
            print("Failed to Delete Standard attachment")
    except Exception as e:
        print(f"Error deleting files: {e}")