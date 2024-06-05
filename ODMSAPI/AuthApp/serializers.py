from rest_framework import serializers
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UserProfileSerializer, self).to_representation(obj)
        ret['status'] = "Active" if obj.is_active else "Inactive"
        ret['department'] = {
                "id":obj.department.id,
                "name":obj.department.name, 
                "department_id":obj.department.department_id
            } if obj.department else None
        return ret
    class Meta:
        model = User
        fields = ["id", "full_name", "profile_photo", "email", "personnel_number", "phone_number", "is_view_manual", "is_view_standard", "is_view_layout", 
                  "is_download_drawing", "is_disable_dwg_file", "last_login", "role", "designation", "is_view_technical_calculation", "is_design_user"]
        read_only_fields = fields
