from django.db import models
from datetime import datetime
import os
import logging
from PIL import Image
from AuthApp.models import User, Unit, Department, Subvolume
from core.utility import getId, extract_sheet_number, get_only_file_name
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
Image.MAX_IMAGE_PIXELS=100000000000000

DRAWING_TYPE_CHOICE = [
    ("PDR", "PDR"),
    ("CDBR", "CDBR"),
    ("RS", "RS"),
    ("PS", "PS"),
    ("FDR", "FDR"),
    ("MISC", "MISC")
]

DRAWING_FILE_TYPE_CHOICE = [
    ("TIF", "TIF"),
    ("PDF", "PDF")
    ]

DRAWING_SIZE_CHOICE = [
    ("A0", "A0"),
    ("A1", "A1"),
    ("A2", "A2"),
    ("A3", "A3"),
    ("A4", "A4")
]

VOLUME_CHOICE = [
    ("1.0", "1.0"),
    ("1.1", "1.1"),
    ("1.2", "1.2")
]

DRAWING_LOG_STATUS_CHOICE = [
    ("View Drawing", "VIEW"),
    ("Add Drawing", "ADD"),
    ("Update Drawing", "UPDATE"),
    ("Archive Drawing", "ARCHIVE"),
    ("Delete Drawing", "DELETE"),
    ("Download Drawing", "DOWNLOAD")
]

logger = logging.getLogger(__name__)

# drawing model
class Drawing(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255, db_index=True)
    default_description = models.TextField(null = True)
    drawing_type = models.CharField(max_length=20, choices=DRAWING_TYPE_CHOICE, default=DRAWING_TYPE_CHOICE[0][0], db_index=True)
    drawing_number = models.CharField(max_length=30, db_index=True)
    drawing_number_numeric = models.BigIntegerField(null=True, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, db_index=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True,db_index=True)
    sub_volume = models.ForeignKey(Subvolume, on_delete=models.SET_NULL, null=True, db_index=True)
    supplier_name = models.CharField(max_length = 250, null=True, db_index=True)
    vendor_number = models.CharField(max_length = 250, null=True, db_index=True)
    client_number = models.CharField(max_length = 250, null=True, db_index=True)
    package_number = models.CharField(max_length=250,null=True, db_index=True)
    work_order_number = models.CharField(max_length=250,null=True, db_index=True)
    revision_version = models.CharField(max_length=30, default = '0')
    drawing_size = models.CharField(max_length=20, choices=DRAWING_SIZE_CHOICE, default=DRAWING_SIZE_CHOICE[0][0])
    drawing_file_type = models.CharField(max_length=20, choices=DRAWING_FILE_TYPE_CHOICE, default=DRAWING_FILE_TYPE_CHOICE[0][0], db_index=True)
    is_layout = models.BooleanField(default = False, db_index=True)
    date_of_registration = models.DateField(null = True)
    certification = models.CharField(max_length=220)
    is_file_present = models.BooleanField(default=False, db_index=True)
    is_dwg_file_present = models.BooleanField(default = False)
    is_approved = models.BooleanField(default=False, db_index=True)
    no_of_sheet = models.IntegerField(default=1)
    remarks = models.TextField()
    is_archive = models.BooleanField(default = False, db_index=True)
    archive_reason = models.TextField(null = True)
    pdr_number = models.CharField(max_length=150, null = True)
    letter_number = models.CharField(max_length=250, null = True)
    fdr_approved_date = models.DateField(null = True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,db_index=True, related_name = 'uploaded_by')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,db_index=True, related_name = 'approved_by')
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('dra_')
            while Drawing.objects.filter(id=self.id).exists():
                self.id = getId('dra_')
        self.drawing_number_numeric = int(''.join(filter(str.isdigit, str(self.drawing_number))) or 0)
        super(Drawing, self).save()
    
def upload_path(instance, filename):
    drawing_type = instance.drawing.drawing_type
    # Construct the upload path dynamically based on the drawing type and filename
    return f'drawings/{drawing_type}/{filename}'

# DrawingFile Model
class DrawingFile(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name='files', db_index=True)
    file = models.FileField(upload_to=upload_path)
    file_name = models.CharField(max_length=255, db_index=True)
    view_pdf_file = models.FileField(upload_to=upload_path, null=True) # only set when file type is .tif create copy of that tif file .pdf
    dwg_file = models.FileField(upload_to=upload_path, null=True) # only set when file type is .tif create copy of that tif file .pdf
    file_size = models.BigIntegerField()
    objects = models.Manager()  # Size of the file in bytes

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('dra_')
            while DrawingFile.objects.filter(id=self.id).exists():
                self.id = getId('dra_')
        if not self.file_size:
            self.file_size = self.file.size

        if not self.file_name:
            self.file_name = get_only_file_name(self.file.name)
        super(DrawingFile, self).save()

    def __str__(self):
        return self.file_name
    
class DrawingDescription(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    index = models.IntegerField()
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE, related_name='description', db_index=True)
    drawing_file = models.ForeignKey(DrawingFile, on_delete=models.SET_NULL, related_name='drawingfile', db_index=True, null=True)
    description = models.TextField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('drd_')
            while DrawingDescription.objects.filter(id=self.id).exists():
                self.id = getId('drd_')
        super(DrawingDescription, self).save()
    
    def __str__(self):
        return self.description
    

class DrawingLog(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    drawing = models.ForeignKey(Drawing, on_delete=models.SET_NULL, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=DRAWING_LOG_STATUS_CHOICE, default=DRAWING_LOG_STATUS_CHOICE[0][0], db_index=True)
    message = models.CharField(max_length=255, db_index=True)
    details = models.TextField()
    action_time = models.DateTimeField(default=datetime.now, db_index=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId("dwl")
            while DrawingLog.objects.filter(id=self.id).exists():
                self.id = getId("dwl")
        super(DrawingLog, self).save()


@receiver(post_save, sender=DrawingFile)
def convert_tif_pdf_post_save(sender, instance, created, **kwargs):
    logger.info(f"sender ${sender} {instance}, {created}, {kwargs}")
    if created:
        if instance.file and instance.drawing.drawing_file_type == "TIF":
            # Open the TIFF file
            tif_file_path = instance.file.path
            if os.path.exists(tif_file_path):
                try:
                    with Image.open(tif_file_path) as img:
                        pdf_file_path = os.path.splitext(tif_file_path)[0] + '.pdf'
                        #img.save(pdf_file_path, "PDF", resolution=100.0)
                        img.save(pdf_file_path, save_all=True)
                        pdf_file_relative_path = os.path.relpath(pdf_file_path, settings.MEDIA_ROOT)
                        instance.view_pdf_file = pdf_file_relative_path
                        instance.save()
                except Exception as e:
                    print(f"Fialed To Convert PDF Drawing{instance.drawing.drawing_number} | File {tif_file_path} {e}")
            else:
                logger.error(f"file not found {tif_file_path} {instance.file.name}")

        # update drawing descptionion with drawing file
        sheet_no = extract_sheet_number(instance.file_name)
        DrawingDescription.objects.filter(drawing = instance.drawing, index = sheet_no).update(drawing_file = instance)



# Define a signal receiver function
@receiver(post_delete, sender=DrawingFile)
def my_model_post_delete(sender, instance, **kwargs):
    try:
        removeDrawingFile(instance)
    except Exception as e:
        logger.error(f"Error deleting files: {e}")


def removeDrawingFile(drawingFile):
    # Delete the associated file from the filesystem
    if drawingFile:
        if drawingFile.file:
            file_path = drawingFile.file.path
            if os.path.isfile(file_path):
                os.remove(file_path)
        if drawingFile.view_pdf_file:
            pdd_path = drawingFile.view_pdf_file.path
            if os.path.isfile(pdd_path):
                os.remove(pdd_path)
        if drawingFile.dwg_file:
            dwg_path = drawingFile.dwg_file.path
            if os.path.isfile(dwg_path):
                os.remove(dwg_path)
        print("Drawing File Is Deleted")
    else:
        print("Drawing File Is Empty")
