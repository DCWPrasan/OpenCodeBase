from rest_framework import serializers
from .models import AutomationJob, PowerLabJob,RepairLabJob, WeighingMaintenanceJob,WeighingOperationJob,CCTVJob, SlideImage
from AuthApp.models import User

class EntryBySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "personnel_number"]
        read_only_fields = fields
        
class EmployeeSearchSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(EmployeeSearchSerializer, self).to_representation(obj)
        ret["label"] = f"{obj.name} ({obj.personnel_number})"
        ret["value"] = obj.id
        return ret
    class Meta:
        model = User
        fields = []
        read_only_fields = fields
        
class EmployeeTableSearchSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'personnel_number', 'role', 'status', 'area', 'is_active']

    def get_area(self, obj):
        if obj.area and isinstance(obj.area, dict):
            names = obj.area.get("name", [])
            if isinstance(names, list):
                return {"name": names}
            elif isinstance(names, str):
                return {"name": [names]}
        return {"name": []}

    def get_status(self, obj):
        return "Active" if obj.is_active else "Inactive"
        

class EmployeeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(EmployeeSerializer, self).to_representation(obj)
        ret["status"] = "Active" if obj.is_active else "Inactive"
        return ret

    class Meta:
        model = User
        fields = ["id", "name", "personnel_number", "role", "area"]
        read_only_fields = fields


class AutomationJobSerializer(serializers.ModelSerializer):
    entry_by = serializers.PrimaryKeyRelatedField(read_only=True)
    modify_by = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret["entry_by"] = EntryBySerializer(obj.entry_by).data if obj.entry_by else None
        ret["modify_by"] = EntryBySerializer(obj.modify_by).data if obj.modify_by else None
        return ret

    class Meta:
        model = AutomationJob
        fields = [
            "id",
            "department",
            "area",
            "job_start_time",
            "job_completion_time",
            "job_description",
            "action_taken",
            "remarks",
            "persons",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]

class PowerLabJobSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(PowerLabJobSerializer, self).to_representation(obj)
        ret["entry_by"] = EntryBySerializer(obj.entry_by).data
        ret["modify_by"] = EntryBySerializer(obj.modify_by).data if obj.modify_by else None
        ret["assigned_staff"] = EntryBySerializer(obj.assigned_staff).data
        ret["present_staffs"] = EntryBySerializer(obj.present_staffs, many=True).data
        return ret

    class Meta:
        model = PowerLabJob
        fields = [
            "id",
            "date",
            "shift",
            "work_order_number",
            "work_order_receive_date",
            "work_order_completion_date",
            "department",
            "assigned_staff",
            "job_description",
            "action_taken",
            "remarks",
            "information_given_department_date",
            "material_handover_department_date",
            "status",
            "created_at",
            "updated_at",
            "is_save_draft"
        ]
        read_only_fields = fields
        extra_kwargs = {
            'date': {'format': '%Y-%m-%d'},
            'work_order_receive_date': {'required': False},
            'work_order_completion_date': {'required': False},
            'information_given_department_date': {'format': '%Y-%m-%d'},
            'material_handover_department_date': {'format': '%Y-%m-%d'},
            'created_at': {'format': '%Y-%m-%d %H:%M:%S'},
            'updated_at': {'format': '%Y-%m-%d %H:%M:%S'},
        }
 
class RepairLabJobSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['entry_by'] = EntryBySerializer(obj.entry_by).data if obj.entry_by else None
        ret['modify_by'] = EntryBySerializer(obj.modify_by).data if obj.modify_by else None
        ret["assigned_staff"] = EntryBySerializer(obj.assigned_staff).data
        ret["present_staffs"] = EntryBySerializer(obj.present_staffs, many=True).data
        return ret

    class Meta:
        model = RepairLabJob
        fields = [
            "id",
            "date",
            "shift",
            "work_order_number",
            "work_order_receive_date",
            "work_order_completion_date",
            "department",
            "job_description",
            "action_taken",
            "remarks",
            "information_given_department_date",
            "material_handover_department_date",
            "status",
            "created_at",
            "updated_at",
            "is_save_draft"
        ]
        read_only_fields = fields
        extra_kwargs = {
            'date': {'format': '%Y-%m-%d'},
            'work_order_receive_date':{'required': False},
            'work_order_completion_date':  {'required': False},
            'information_given_department_date': {'format': '%Y-%m-%d'},
            'material_handover_department_date': {'format': '%Y-%m-%d'},
            'created_at': {'format': '%Y-%m-%d %H:%M:%S'},
            'updated_at': {'format': '%Y-%m-%d %H:%M:%S'},
        }
        
class WeighingMaintenanceJobSerializer(serializers.ModelSerializer):
    assigned_staff = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False,
        allow_null=True
    )
    present_staffs = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['entry_by'] = EntryBySerializer(obj.entry_by).data if obj.entry_by else None
        ret["assigned_staff"] = EntryBySerializer(obj.assigned_staff).data if obj.assigned_staff else None
        ret["present_staffs"] = EntryBySerializer(obj.present_staffs.all(), many=True).data
        ret["modify_by"] = EntryBySerializer(obj.modify_by).data if obj.modify_by else None
        return ret

    class Meta:
        model = WeighingMaintenanceJob
        fields = [
            "id",
            "date",
            "shift",
            "complaint_time",
            "complaint_nature",
            "weighbridge_location",
            "reported_by",
            "action_taken",
            "remarks",
            "present_staffs",
            "assigned_staff",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]
        
class WeighingOperationJobSerializer(serializers.ModelSerializer):
    assigned_staff = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False,
        allow_null=True
    )
    present_staffs = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['entry_by'] = EntryBySerializer(obj.entry_by).data if obj.entry_by else None
        ret["assigned_staff"] = EntryBySerializer(obj.assigned_staff).data if obj.assigned_staff else None
        ret["present_staffs"] = EntryBySerializer(obj.present_staffs.all(), many=True).data
        ret["modify_by"] = EntryBySerializer(obj.modify_by).data if obj.modify_by else None
        return ret

    class Meta:
        model = WeighingOperationJob
        fields = [
            "id",
            "date",
            "shift",
            "source",
            "commodity",
            "wb_register_number",
            "rake",
            "number_of_wagon",
            "gross_weight",
            "net_weight",
            "rake_in_time",
            "system_one",
            "system_two",
            "general",
            "present_staffs",
            "assigned_staff",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]
        
class CCTVJobSerializer(serializers.ModelSerializer):
    present_staffs = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret["entry_by"] = EntryBySerializer(obj.entry_by).data if obj.entry_by else None
        ret["modify_by"] = EntryBySerializer(obj.modify_by).data if obj.modify_by else None
        ret["present_staffs"] = EntryBySerializer(obj.present_staffs.all(), many=True).data
        return ret

    class Meta:
        model = CCTVJob
        fields = [
            "id",
            "date",
            "shift",
            "present_staffs",
            "supporting_staff",
            "complain_site",
            "complain_received_time",
            "complain_nature",
            "complain_details",
            "action_taken",
            "completion_time",
            "remarks",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "entry_by",
            "modify_by",
            "created_at",
            "updated_at",
        ]   
        
        
class ReportFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    site = serializers.CharField(required=False)
    job_nature = serializers.CharField(required=False)
    shift = serializers.CharField(required=False)
    report_type = serializers.ChoiceField(
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('calendar_year', 'Calendar Year'),
            ('financial_year', 'Financial Year'),
            ('custom', 'Custom')
        ],
        required=True
    )
    year = serializers.IntegerField(required=False)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)
    week = serializers.IntegerField(required=False, min_value=1, max_value=53)


class SlideImageSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        request = self.context.get('request')
        ret["image"] = request.build_absolute_uri(obj.image.url)
        ret["uploaded_by"] = EntryBySerializer(obj.uploaded_by).data
        ret["is_currently_displayable"] = obj.is_currently_displayable
        ret["is_deletable"] = request.user.is_superuser or obj.uploaded_by == request.user
        return ret

    class Meta:
        model = SlideImage
        fields = ["id", "display_until", "image", "uploaded_by"]  

class ScreenerSlidesSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        request = self.context.get('request')
        ret["image"] = request.build_absolute_uri(obj.image.url)
        return ret

    class Meta:
        model = SlideImage
        fields = ["id", "image"] 