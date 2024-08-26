from datetime import datetime
from django.db import models
from AuthApp.models import Department, Unit, User
from core.utility import getId
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
# Create your models here.

SIR_LOG_STATUS_CHOICE = [
    ("View SIR", "VIEW"),
    ("Add SIR", "ADD"),
    ("Update SIR", "UPDATE"),
    ("Archive SIR", "ARCHIVE"),
    ("Delete SIR", "DELETE"),
]

STABILITY_CERTIFICATION_LOG_STATUS_CHOICE = [
    ("View Stability Certificate", "VIEW"),
    ("Add Stability Certificatie", "ADD"),
    ("Update Stability Certificatie", "UPDATE"),
    ("Archive Stability Certificatie", "ARCHIVE"),
    ("Delete Stability Certificatie", "DELETE"),
]

COMPLIANCE_LOG_STATUS_CHOICE = [
    ("View Compliance", "VIEW"),
    ("Add Compliance", "ADD"),
    ("Update Compliance", "UPDATE"),
    ("Archive Compliance", "ARCHIVE"),
    ("Delete Compliance", "DELETE"),
]


DOCUMENT_LOG_STATUS_CHOICE = [
    ("View Document", "VIEW"),
    ("Add Document", "ADD"),
    ("Update Document", "UPDATE"),
    ("Archive Document", "ARCHIVE"),
    ("Delete Document", "DELETE"),
]


class SIR(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False, db_index=True)
    sir_number = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    agency = models.CharField(max_length=220, null=True)
    year_of_inspection = models.CharField(max_length=10)
    compliance = models.CharField(max_length=3)
    description = models.TextField(null=True)
    attachment = models.FileField(upload_to="sir/")
    created_at = models.DateTimeField(default=datetime.now)
    is_archive = models.BooleanField(default=False)
    archive_reason = models.TextField(null = True)
    is_approved = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('sir_')
            while SIR.objects.filter(id=self.id).exists():
                self.id = getId('sir_')
        super(SIR, self).save()

# SIR Log
class SIRLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sir = models.ForeignKey(SIR, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=SIR_LOG_STATUS_CHOICE, default=SIR_LOG_STATUS_CHOICE[0][0])
    message = models.CharField(max_length=255)
    details = models.TextField()
    action_time = models.DateTimeField(default=datetime.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("sirl")
            while SIRLog.objects.filter(id=self.id).exists():
                self.id = getId("sirl")
        super(SIRLog, self).save()

    
class StabilityCertification(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False, db_index=True)
    certificate_number = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    agency = models.CharField(max_length=220, null=True)
    attachment = models.FileField(upload_to="stabilitycertification/")
    created_at = models.DateTimeField(default=datetime.now)
    is_archive = models.BooleanField(default=False)
    archive_reason = models.TextField(null = True)
    is_approved = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('stc_')
            while StabilityCertification.objects.filter(id=self.id).exists():
                self.id = getId('stc_')
        super(StabilityCertification, self).save()

# Stability Certificate Log
class StabilityCertificationLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stability_certification = models.ForeignKey(StabilityCertification, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, choices=STABILITY_CERTIFICATION_LOG_STATUS_CHOICE, default=STABILITY_CERTIFICATION_LOG_STATUS_CHOICE[0][0])
    message = models.CharField(max_length=255)
    details = models.TextField()
    action_time = models.DateTimeField(default=datetime.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("stcl")
            while StabilityCertificationLog.objects.filter(id=self.id).exists():
                self.id = getId("stcl")
        super(StabilityCertificationLog, self).save()
    

class Compliance(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False, db_index=True)
    reference_number = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to="compliance/")
    created_at = models.DateTimeField(default=datetime.now)
    is_archive = models.BooleanField(default=False)
    archive_reason = models.TextField(null = True)
    is_approved = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('com_')
            while Compliance.objects.filter(id= self.id).exists():
                self.id = getId('com_')
        super(Compliance, self).save()


class ComplianceLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    compliance = models.ForeignKey(Compliance, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=COMPLIANCE_LOG_STATUS_CHOICE, default=COMPLIANCE_LOG_STATUS_CHOICE[0][0])
    message = models.CharField(max_length=255)
    details = models.TextField()
    action_time = models.DateTimeField(default=datetime.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("coml")
            while ComplianceLog.objects.filter(id=self.id).exists():
                self.id = getId("coml")
        super(ComplianceLog, self).save()

    
class Document(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False, db_index=True)
    document_number = models.CharField(max_length=100)
    description = models.TextField()
    attachment = models.FileField(upload_to="document/")
    created_at = models.DateTimeField(default=datetime.now)
    is_archive = models.BooleanField(default=False)
    archive_reason = models.TextField(null = True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('doc_')
            while Document.objects.filter(id= self.id).exists():
                self.id = getId('doc_')
        super(Document, self).save()


class DocumentLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=DOCUMENT_LOG_STATUS_CHOICE, default=DOCUMENT_LOG_STATUS_CHOICE[0][0])
    message = models.CharField(max_length=255)
    details = models.TextField()
    action_time = models.DateTimeField(default=datetime.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("docl")
            while DocumentLog.objects.filter(id=self.id).exists():
                self.id = getId("docl")
        super(DocumentLog, self).save()
        
        
        


# Define a signal receiver function
@receiver(post_delete, sender=SIR)
def sir_model_post_delete(sender, instance, **kwargs):
    try:
        if instance.attachment:
            file_path = instance.attachment.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        else:
            print("Failed to Delete SIR attachment")
    except Exception as e:
        print(f"Error deleting files: {e}")
        
    
    
@receiver(post_delete, sender=StabilityCertification)
def stability_certification_model_post_delete(sender, instance, **kwargs):
    try:
        if instance.attachment:
            file_path = instance.attachment.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        else:
            print("Failed to Delete Stability Certification attachment")
    except Exception as e:
        print(f"Error deleting files: {e}")
        
        
        
@receiver(post_delete, sender=Compliance)
def compliance_model_post_delete(sender, instance, **kwargs):
    try:
        if instance.attachment:
            file_path = instance.attachment.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        else:
            print("Failed to Delete Compliance attachment")
    except Exception as e:
        print(f"Error deleting files: {e}")
