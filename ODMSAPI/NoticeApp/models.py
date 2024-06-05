from datetime import datetime
from django.db import models
from core.utility import getId
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os




class Notice(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    notice = models.TextField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('not_')
            while Notice.objects.filter(id= self.id).exists():
                self.id = getId('not_')
        super(Notice, self).save()

      
class Slider(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    media = models.FileField(upload_to="slider/")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('sli_')
            while Slider.objects.filter(id = self.id).exists():
                self.id = getId('sli_')
        super(Slider, self).save()


class NewUserRequest(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    personnel_number = models.IntegerField(unique=True)
    full_name = models.CharField(max_length=50)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    designation = models.CharField(max_length=150)
    department = models.CharField(max_length=150)
    cost_code_department = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('nur_')
            while NewUserRequest.objects.filter(id = self.id).exists():
                self.id = getId('nur_')
        super(NewUserRequest, self).save()
        



# Define a signal receiver function

@receiver(post_delete, sender=Slider)
def slider_model_post_delete(sender, instance, **kwargs):
    try:
        if instance.media:
            file_path = instance.media.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        else:
            print("Failed to Delete Slider attachment")
    except Exception as e:
        print(f"Error deleting files: {e}")