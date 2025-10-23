from django.db import models
from AuthApp.utils import getId
from AuthApp.models import User
from django.utils import timezone

SHIFT_TYPE_CHOICE = [
    ("General Shift", "GENERAL SHIFT"),
    ("A Shift", "A SHIFT"),
    ("B Shift", "B SHIFT"),
    ("C Shift", "C SHIFT"),
]

LAB_STATUS_CHOICES= [
    ("In Progress", "In Progress"),
    ("Completed", "Completed"),
    ("Beyond Repair", "Beyond Repair"),
    ("Taken Back", "Taken Back")
]
COMPLAINT_CHOICES = [
    ('INSPECTION OF WBS', 'INSPECTION OF WBS'),
    ('PREVENTIVE MAINTENANCE OF WBS', 'PREVENTIVE MAINTENANCE OF WBS'),
    ('CALIBRATION CHECKING OF WBS', 'CALIBRATION CHECKING OF WBS'),
    ('PRE-STAMPING CHECKING OF WBS', 'PRE-STAMPING CHECKING OF WBS'),
    ('VERIFICATION & STAMPING OF WBS', 'VERIFICATION & STAMPING OF WBS'),
    ('SERVICE SUPPORT', 'SERVICE SUPPORT'),
]

LOCATION_CHOICES = [
    ('20T M-17 SWPP PF WB', '20T M-17 SWPP PF WB'),
    ('AB-BAY STATIC RAIL WB PF-A/B/C', 'AB-BAY STATIC RAIL WB PF-A/B/C'),
    ('BC-BAY STATIC RAIL WB PF-A/B/C', 'BC-BAY STATIC RAIL WB PF-A/B/C'),
    ('CD-BAY STATIC RAIL WB', 'CD-BAY STATIC RAIL WB'),
    ('CEMENT STORE 40T ROAD WB', 'CEMENT STORE 40T ROAD WB'),
    ('CRM 30T RS-BAY(SHIPPING) PF WB', 'CRM 30T RS-BAY(SHIPPING) PF WB'),
    ('GRILL GATE 150T RAIL I/M WB LINE#241', 'GRILL GATE 150T RAIL I/M WB LINE#241'),
    ('GRILL GATE 150T RAIL I/M WB LINE#243', 'GRILL GATE 150T RAIL I/M WB LINE#243'),
    ('HK GATE(NEW) 40T ROAD WB', 'HK GATE(NEW) 40T ROAD WB'),
    ('HK GATE(OLD) 50T ROAD WB', 'HK GATE(OLD) 50T ROAD WB'),
    ('HM 200T STATIC RAIL WB PCM LINE', 'HM 200T STATIC RAIL WB PCM LINE'),
    ('HM 250T STATIC RAIL WB PF-A', 'HM 250T STATIC RAIL WB PF-A'),
    ('HM 250T STATIC RAIL WB PF-B', 'HM 250T STATIC RAIL WB PF-B'),
    ('HM 800T STATIC RAIL WB LINE#1 WB-1 & WB-2', 'HM 800T STATIC RAIL WB LINE#1 WB-1 & WB-2'),
    ('HM 800T STATIC RAIL WB LINE#2 WB-1 & WB-2', 'HM 800T STATIC RAIL WB LINE#2 WB-1 & WB-2'),
    ('HSM-1 30T NEW DIVIDING LINE PF WB', 'HSM-1 30T NEW DIVIDING LINE PF WB'),
    ('HSM-2 COIL CONVEYER WEIGHING SYS.', 'HSM-2 COIL CONVEYER WEIGHING SYS.'),
    ('HSM-2 COIL YARD PF WB-1', 'HSM-2 COIL YARD PF WB-1'),
    ('HSM-2 COIL YARD PF WB-2', 'HSM-2 COIL YARD PF WB-2'),
    ('HSM-2 SSL PF WB-3', 'HSM-2 SSL PF WB-3'),
    ('NCCY 140T RAIL I/M WB', 'NCCY 140T RAIL I/M WB'),
    ('NEW SGP GATE 100T ROAD WB', 'NEW SGP GATE 100T ROAD WB'),
    ('NEW TARAPUR GATE 100T ROAD WB', 'NEW TARAPUR GATE 100T ROAD WB'),
    ('NPM 100T ROAD WB-1', 'NPM 100T ROAD WB-1'),
    ('NPM 100T ROAD WB-2', 'NPM 100T ROAD WB-2'),
    ('NPM STATIC RAIL WB PF-A/B/C', 'NPM STATIC RAIL WB PF-A/B/C'),
    ('RECEPTION YARD 150T RAIL I/M WB-1', 'RECEPTION YARD 150T RAIL I/M WB-1'),
    ('RECEPTION YARD 150T RAIL I/M WB-2', 'RECEPTION YARD 150T RAIL I/M WB-2'),
    ('SSD 100T ROAD WB', 'SSD 100T ROAD WB'),
    ('SSD 140T RAIL I/M WB', 'SSD 140T RAIL I/M WB'),
    ('SSM 20T HJ-BAY PF WB', 'SSM 20T HJ-BAY PF WB'),
    ('SSM 20T JK-BAY PF WB', 'SSM 20T JK-BAY PF WB'),
    ('SSSY 100T ROAD WB', 'SSSY 100T ROAD WB'),
    ('SSSY 60T ROAD WB', 'SSSY 60T ROAD WB'),
]
CONSIGNOR_CHOICES = [
    ('ACCJ', 'ACCJ'),
    ('ANDAL', 'ANDAL'),
    ('ASANSOL', 'ASANSOL'),
    ('B&CS', 'B&CS'),
    ('BACHRA', 'BACHRA'),
    ('BARSUA', 'BARSUA'),
    ('BASRA', 'BASRA'),
    ('BBLS', 'BBLS'),
    ('BCME', 'BCME'),
    ('BCNA', 'BCNA'),
    ('BCNEMPTY', 'BCNEMPTY'),
    ('BCLP', 'BCLP'),
    ('BELHA DOLO', 'BELHA DOLO'),
    ('BHP', 'BHP'),
    ('BHARDWAR', 'BHARDWAR'),
    ('BHUJUDI', 'BHUJUDI'),
    ('BOCM', 'BOCM'),
    ('BOCP', 'BOCP'),
    ('BOCPJ', 'BOCPJ'),
    ('BRMP', 'BRMP'),
    ('BSPC', 'BSPC'),
    ('BSCE', 'BSCE'),
    ('BSCS', 'BSCS'),
    ('BSPE', 'BSPE'),
    ('BUBLI', 'BUBLI'),
    ('BUA', 'BUA'),
    ('CDA', 'CDA'),
    ('CHAINPURA', 'CHAINPURA'),
    ('CHANDERPUR', 'CHANDERPUR'),
    ('CHRM', 'CHRM'),
    ('DCDL', 'DCDL'),
    ('DCSD', 'DCSD'),
    ('DHAMARA', 'DHAMARA'),
    ('DGCW', 'DGCW'),
    ('DPCP', 'DPCP'),
    ('DPEY', 'DPEY'),
    ('DSEY', 'DSEY'),
    ('DUGDHA', 'DUGDHA'),
    ('DURGAPUR', 'DURGAPUR'),
    ('FSNL', 'FSNL'),
    ('GERMAN', 'GERMAN'),
    ('GFMK', 'GFMK'),
    ('HALDIA', 'HALDIA'),
    ('JABADABA', 'JABADABA'),
    ('JBCT', 'JBCT'),
    ('JBO', 'JBO'),
    ('JCPP', 'JCPP'),
    ('JDWS', 'JDWS'),
    ('KATRA', 'KATRA'),
    ('KCKT', 'KCKT'),
    ('KFNT', 'KFNT'),
    ('KIRIBURU', 'KIRIBURU'),
    ('KJME', 'KJME'),
    ('KMME', 'KMME'),
    ('KONICA', 'KONICA'),
    ('KPDOCK', 'KPDOCK'),
    ('KTH', 'KTH'),
    ('KSBJ', 'KSBJ'),
    ('KSNT', 'KSNT'),
    ('KTO', 'KTO'),
    ('KTN', 'KTN'),
    ('LAIKERA', 'LAIKERA'),
    ('LNC', 'LNC'),
    ('LOCM', 'LOCM'),
    ('MADHUBAN', 'MADHUBAN'),
    ('MDBN', 'MDBN'),
    ('MELG', 'MELG'),
    ('MFSJ', 'MFSJ'),
    ('MISCLANEOUS', 'MISCLANEOUS'),
    ('MLD', 'MLD'),
    ('MLTC', 'MLTC'),
    ('MGPB', 'MGPB'),
    ('MGPV', 'MGPV'),
    ('MOCL', 'MOCL'),
    ('MUNIDIHI', 'MUNIDIHI'),
    ('NANDAN', 'NANDAN'),
    ('NHSB', 'NHSB'),
    ('NJTC', 'NJTC'),
    ('NMC', 'NMC'),
    ('OCIG', 'OCIG'),
    ('OTHERS', 'OTHERS'),
    ('PATHARDIHI', 'PATHARDIHI'),
    ('PAW', 'PAW'),
    ('PBJT', 'PBJT'),
    ('PBCP', 'PBCP'),
    ('PCLE', 'PCLE'),
    ('PCME', 'PCME'),
    ('PBLF', 'PBLF'),
    ('PBRP', 'PBRP'),
    ('PSEC', 'PSEC'),
    ('PSCE', 'PSCE'),
    ('PSMM', 'PSMM'),
    ('PSTE', 'PSTE'),
    ('RAJARAPPA', 'RAJARAPPA'),
    ('RANI GANJ', 'RANI GANJ'),
    ('RAY', 'RAY'),
    ('RJCB', 'RJCB'),
    ('ROXL', 'ROXL'),
    ('ROXY', 'ROXY'),
    ('RSP', 'RSP'),
    ('RWR', 'RWR'),
    ('SAMLA SIDEING', 'SAMLA SIDEING'),
    ('SARDEGA', 'SARDEGA'),
    ('SARUBERA', 'SARUBERA'),
    ('SCSK', 'SCSK'),
    ('SCSC', 'SCSC'),
    ('SGP', 'SGP'),
    ('SMPR', 'SMPR'),
    ('SNFC', 'SNFC'),
    ('SNWG', 'SNWG'),
    ('SONU', 'SONU'),
    ('SWANG', 'SWANG'),
    ('TAPASI', 'TAPASI'),
    ('TARACIA', 'TARACIA'),
    ('TEST CAR', 'TEST CAR'),
    ('TSBD', 'TSBD'),
    ('UCPD', 'UCPD'),
    ('UPCD', 'UPCD'),
    ('VIZAG', 'VIZAG'),
    ('VNHL', 'VNHL'),
    ('VZP', 'VZP'),
]

COMMODITY_CHOICES = [
    ('TEST', 'TEST'),
    ('COAL', 'COAL'),
    ('SILICO MANGANEESE', 'SILICO MANGANEESE'),
    ('HARDCOKE', 'HARDCOKE'),
    ('LD SLAG', 'LD SLAG'),
    ('BF FINES', 'BF FINES'),
    ('SCRAP', 'SCRAP'),
    ('LD FINES', 'LD FINES'),
    ('MISCLANEOUS', 'MISCLANEOUS'),
    ('SINTER', 'SINTER'),
    ('SLAG', 'SLAG'),
    ('IRON ORE', 'IRON ORE'),
    ('G. SLAG', 'G. SLAG'),
    ('IRON ORE LUMPS', 'IRON ORE LUMPS'),
    ('EMPTY', 'EMPTY'),
    ('LIMESTONE', 'LIMESTONE'),
    ('QUARTZ', 'QUARTZ'),
    ('DOLOMITE', 'DOLOMITE'),
    ('IRON ORE PELLET', 'IRON ORE PELLET'),
    ('MANGANEESE ORE', 'MANGANEESE ORE'),
    ('LD FINES & BF FINES', 'LD FINES & BF FINES'),
    ('HARDCOKE,MBC,MIXED HARD', 'HARDCOKE,MBC,MIXED HARD'),
    ('BREEZE COKE', 'BREEZE COKE'),
    ('LIMESTONE SONU', 'LIMESTONE SONU'),
    ('IRON ORE FINES', 'IRON ORE FINES'),
    ('BOILER COAL', 'BOILER COAL'),
    ('OTHERS', 'OTHERS'),
]
JOB_TYPE_CHOICES = [
    ('PM', 'PM'),
    ('BREAKDOWN', 'BREAKDOWN'),
    ('RELOCATION', 'RELOCATION'),
    ('DISMANTLING', 'DISMANTLING'), 
    ('NEW INSTALLATION', 'NEW INSTALLATION'),
    ('OTHERS', 'OTHERS'),
]

DEPARTMENT_LIST = [
    ('BLAST FURNACE', 'BLAST FURNACE'),
    ('STEEL MELTING SHOP', 'STEEL MELTING SHOP'),
    ('HOT STRIP MILL', 'HOT STRIP MILL'),
    ('COLD ROLLING MILL', 'COLD ROLLING MILL'),
    ('PLATE MILL', 'PLATE MILL'),
    ('COKE OVENS AND BY-PRODUCT PLANT', 'COKE OVENS AND BY-PRODUCT PLANT'),
    ('SINTER PLANT', 'SINTER PLANT'),
    ('OXYGEN PLANT', 'OXYGEN PLANT'),
    ('MAINTENANCE AND REPAIR', 'MAINTENANCE AND REPAIR'),
    ('QUALITY CONTROL', 'QUALITY CONTROL'),
]
PR_DEPARTMENT_LIST = [
    ('AC', 'AC'),
    ('BFs', 'BFs'),
    ('CCD', 'CCD'),
    ('CED', 'CED'),
    ('CES', 'CES'),
    ('COKE OVENs', 'COKE OVENs'),
    ('CP-2', 'CP-2'),
    ('CPP-1', 'CPP-1'),
    ('DESIGN', 'DESIGN'),
    ('HRDC', 'HRDC'),
    ('HSM-2', 'HSM-2'),
    ('I&A (INSTRUMENTATION)', 'I&A (INSTRUMENTATION)'),
    ('LDBP', 'LDBP'),
    ('Mines (BIM,BOM,KIM)', 'Mines (BIM,BOM,KIM)'),
    ('NPM', 'NPM'),
    ('PD', 'PD'),
    ('PIPE PLANTs', 'PIPE PLANTs'),
    ('PM', 'PM'),
    ('R&C LAB', 'R&C LAB'),
    ('RMHP', 'RMHP'),
    ('Roll shop', 'Roll shop'),
    ('RS (E)', 'RS (E)'),
    ('SHOPs', 'SHOPs'),
    ('SMS-1', 'SMS-1'),
    ('SMS-2', 'SMS-2'),
    ('SP-1', 'SP-1'),
    ('SP-2', 'SP-2'),
    ('SP-3', 'SP-3'),
    ('SPP', 'SPP'),
    ('SSM', 'SSM'),
    ('TOP-2', 'TOP-2'),
    ('Town Engg (E)', 'Town Engg (E)'),
    ('Transport & FMM', 'Transport & FMM'),
    ('TRM', 'TRM'),
    ('WMD', 'WMD'),

]




class AutomationJob(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    department = models.CharField(max_length=250, choices=PR_DEPARTMENT_LIST, db_index=True)
    area = models.CharField(max_length=250, db_index=True)
    job_start_time = models.DateTimeField()
    job_completion_time = models.DateTimeField()
    job_description = models.TextField()
    action_taken = models.TextField()
    remarks = models.TextField()
    persons = models.TextField()   
    entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="automation_entry_by", db_index=True)
    modify_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="automation_modify_by", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('auj_')
            while AutomationJob.objects.filter(id=self.id).exists():
                self.id = getId('auj_')
        super(AutomationJob, self).save()

class PowerLabJob(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    date = models.DateField()
    shift = models.CharField(max_length=15, choices=SHIFT_TYPE_CHOICE)
    work_order_number = models.CharField(max_length=50)
    work_order_receive_date = models.DateField(null=True, blank=True)  # Made optional
    work_order_completion_date = models.DateField(null=True, blank=True)  # Made optional
    department = models.CharField(max_length=250,choices=PR_DEPARTMENT_LIST, db_index=True)
    present_staffs = models.ManyToManyField(User, related_name="powerlab_present_staffs")
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="powerlab_assigned_staff")
    job_description = models.TextField()
    action_taken = models.TextField()
    remarks = models.TextField()
    information_given_department_date = models.DateField(null=True, blank=True)   
    material_handover_department_date = models.DateField(null=True, blank=True)      
    status = models.CharField(choices=LAB_STATUS_CHOICES, max_length=50, db_index=True)
    entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="powerlab_entry_by", db_index=True)
    modify_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="powerlab_modify_by", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed to auto_now for updates
    is_save_draft = models.BooleanField(default=False)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('plj_')
            while PowerLabJob.objects.filter(id=self.id).exists():
                self.id = getId('plj_')
        
        # Clear completion dates if status is "In Progress"
        if self.status == "In Progress":
            self.work_order_completion_date = None
            self.material_handover_department_date = None
            
        super(PowerLabJob, self).save(*args, **kwargs)

class RepairLabJob(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    date = models.DateField()
    shift = models.CharField(max_length=15, choices=SHIFT_TYPE_CHOICE)
    work_order_number = models.CharField(max_length=50)
    work_order_receive_date = models.DateField(null=True, blank=True)  # Made optional
    work_order_completion_date = models.DateField(null=True, blank=True)  # Made optional
    department = models.CharField(max_length=250,choices=PR_DEPARTMENT_LIST, db_index=True)
    present_staffs = models.ManyToManyField(User, related_name="repairlab_present_staffs")
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="repairlab_assigned_staff")
    job_description = models.TextField()
    action_taken = models.TextField()
    remarks = models.TextField()
    information_given_department_date = models.DateField(null=True, blank=True)   
    material_handover_department_date = models.DateField(null=True, blank=True)      
    status = models.CharField(choices=LAB_STATUS_CHOICES, max_length=50, db_index=True)
    entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="repairlab_entry_by", db_index=True)
    modify_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="repairlab_modify_by", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_save_draft = models.BooleanField(default=False)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('rlj_')
            while RepairLabJob.objects.filter(id=self.id).exists():
                self.id = getId('rlj_')
        
        # Clear completion dates if status is "In Progress"
        if self.status == "In Progress":
            self.work_order_completion_date = None
            self.material_handover_department_date = None
            
        super(RepairLabJob, self).save(*args, **kwargs)
       
class WeighingMaintenanceJob(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    date = models.DateField()
    shift = models.CharField(max_length=15, choices=SHIFT_TYPE_CHOICE)
    complaint_time = models.DateTimeField()
    complaint_nature = models.CharField(max_length=250,verbose_name="Nature/Details of Complaint",choices=COMPLAINT_CHOICES)
    weighbridge_location = models.CharField(max_length=250,verbose_name="Location of Weighbridge",choices=LOCATION_CHOICES)
    reported_by = models.TextField(verbose_name="Reported By/From")
    action_taken = models.TextField(verbose_name="Action Taken")
    remarks = models.TextField(verbose_name="Remarks")
    present_staffs = models.ManyToManyField(User, related_name="weighing_maintenance_present_staffs")
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="weighing_maintenance_assigned_staff")
    entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="weighing_maintenance_entry_by", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modify_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="weighing_maintenance_modify_by")
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('wmj_')
            while WeighingMaintenanceJob.objects.filter(id=self.id).exists():
                self.id = getId('wmj_')
        super(WeighingMaintenanceJob, self).save()
        
        



class WeighingOperationJob(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    date = models.DateField()
    shift = models.CharField(max_length=15, choices=SHIFT_TYPE_CHOICE)
    source = models.CharField(max_length=250,verbose_name="source/Consignor",choices=CONSIGNOR_CHOICES)
    commodity = models.CharField(max_length=250,verbose_name="Location of Weighbridge",choices=COMMODITY_CHOICES)
    wb_register_number = models.CharField(max_length=250,verbose_name="WB Register No")
    rake = models.CharField(max_length=250,verbose_name="Rake No")
    number_of_wagon = models.CharField(max_length=250,verbose_name="No Of Wagon")
    gross_weight = models.CharField(max_length=250,verbose_name="Gross Weight in Tonnes")
    net_weight = models.CharField(max_length=250,verbose_name="Net Weight in Tonnes")
    rake_in_time = models.DateTimeField(verbose_name="Rake In Time")
    system_one = models.TextField(verbose_name="System-1 /WB-1 status")
    system_two = models.TextField(verbose_name="System-2 /WB-2 status")
    general = models.TextField(verbose_name="General")
    present_staffs = models.ManyToManyField(User, related_name="weighing_operation_present_staffs")
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="weighing_operation_assigned_staff")
    entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="weighing_operation_entry_by", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modify_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="weighing_operation_modify_by")
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = getId('woj_')
            while WeighingOperationJob.objects.filter(id=self.id).exists():
                self.id = getId('woj_')
        super(WeighingOperationJob, self).save()
        
class CCTVJob(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    date = models.DateField()
    shift = models.CharField(max_length=15, choices=SHIFT_TYPE_CHOICE)
    present_staffs = models.ManyToManyField(User, related_name='cctv_jobs_present')
    supporting_staff=models.CharField(max_length=250,verbose_name="Supporting Staff")  
    complain_site=models.CharField(max_length=250,verbose_name="Complain Site")
    complain_received_time=models.DateTimeField(verbose_name="Complain Received Time")
    complain_nature=models.TextField(verbose_name="Nature of Complain",choices=JOB_TYPE_CHOICES)      
    complain_details=models.TextField(verbose_name="Details of Complain")  
    action_taken=models.TextField(verbose_name="Action Taken")
    completion_time=models.DateTimeField(verbose_name="Completion Time")
    remarks=models.TextField(verbose_name="Remarks")
    entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="cctv_entry_by", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modify_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="cctv_modify_by")
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def save(self,*args, **kwargs):
        if not self.id:
            self.id = getId('ctj_')
            while CCTVJob.objects.filter(id=self.id).exists():
                self.id = getId('ctj_')
        super(CCTVJob, self).save()
        
        
class SlideImage(models.Model):
    id = models.CharField(editable=False, primary_key=True, max_length=255)
    image = models.ImageField(upload_to='slideshow_images/')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_slides'
    )
    display_until = models.DateField(
        null=True,
        blank=True,
        help_text="Date until which the image should be displayed. If null, it displays indefinitely."
    )
    upload_date = models.DateTimeField(auto_now_add=True)

    @property
    def is_currently_displayable(self):
        """Checks if the image should be displayed today."""
        if self.display_until is None:
            return True
        return self.display_until >= timezone.now().date()

    def __str__(self):
        return f"Slide {self.id} by {self.uploaded_by.username}"
    
    def save(self,*args, **kwargs):
        if not self.id:
            self.id = getId('sim_')
            while SlideImage.objects.filter(id=self.id).exists():
                self.id = getId('sim_')
        super(SlideImage, self).save()


