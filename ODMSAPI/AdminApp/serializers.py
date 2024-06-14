from rest_framework import serializers
from AuthApp.models import User, Unit, Department, LogInOutLog, Subvolume,Volume

class TotalUserListSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(TotalUserListSerializer, self).to_representation(obj)
        ret['department'] = obj.department.name if obj.department else None
        return ret
    
    class Meta:
        model = User
        fields = ["full_name", "personnel_number", "designation"]
        read_only_fields = fields


class UserListSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UserListSerializer, self).to_representation(obj)
        ret['status'] = "Active" if obj.is_active else "Inactive"
        ret['department'] = {
                "id":obj.department.department_id,
                "name":obj.department.name, 
                "department_id":obj.department_id
            } if obj.department else None
        return ret
    class Meta:
        model = User
        fields = ["id", "full_name", "email",  "personnel_number", "phone_number", "role", "designation"]
        read_only_fields = fields

class UserDetailSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UserDetailSerializer, self).to_representation(obj)
        ret['status'] = "Active" if obj.is_active else "Inactive"
        ret['department'] = {
                "id":obj.department.id,
                "name":obj.department.name, 
                "department_id":obj.department.department_id
            } if obj.department else None
        return ret
    class Meta:
        model = User
        fields = ["id", "full_name", "profile_photo", "email", "personnel_number",
                  "phone_number", "last_login", "role", "designation",
                  "drawing_permission", "standard_permission", "document_permission"]
        read_only_fields = fields


class UserLoginLogoutLogListSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(UserLoginLogoutLogListSerializer, self).to_representation(obj)
        ret['user'] = {
            "id":obj.user.id,
            "full_name":obj.user.full_name,
            "personnel_number":obj.user.personnel_number,
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = LogInOutLog
        fields = ["id", "message", "details", "device_info"]
        read_only_fields = fields


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "department_id", "name"]
        read_only_fields = fields

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "unit_id", "name"]
        read_only_fields = fields

class SubVolumeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SubVolumeSerializer, self).to_representation(obj)
        ret['volume'] = {
            "id":obj.volume.id,
            "name":obj.volume.name
        }
        return ret
    class Meta:
        model = Subvolume
        fields = ["id", "sub_volume_no", "name"]
        read_only_fields = fields

class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = ["id", "name", "volume_id"]
        read_only_fields = fields


### all search related dropdown api
class SearchUnitSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchUnitSerializer, self).to_representation(obj)
        ret['label'] = obj.name
        ret['value'] = obj.unit_id
        return ret

    class Meta:
        model = Unit
        fields = []
        read_only_fields = fields

class SearchDepartmentSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchDepartmentSerializer, self).to_representation(obj)
        ret['label'] = obj.name
        ret['value'] = obj.department_id
        return ret

    class Meta:
        model = Department
        fields = []
        read_only_fields = fields
        
class SearchVolumeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchVolumeSerializer, self).to_representation(obj)
        ret['label'] = obj.sub_volume_no
        ret['value'] = obj.sub_volume_no
        return ret

    class Meta:
        model = Subvolume
        fields = []
        read_only_fields = fields
        
class SearchRSVolumeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchRSVolumeSerializer, self).to_representation(obj)
        ret['label'] = obj.name
        ret['value'] = obj.id
        return ret

    class Meta:
        model = Volume
        fields = []
        read_only_fields = fields


class SearchUserSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(SearchUserSerializer, self).to_representation(obj)
        ret['label'] = f'{obj.full_name} ({obj.personnel_number})'
        ret['value'] = obj.id
        return ret

    class Meta:
        model = User
        fields = []
        read_only_fields = fields


