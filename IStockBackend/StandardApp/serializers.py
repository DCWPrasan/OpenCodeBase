from rest_framework import serializers
from .models import Standard,RSNVolume,RSNGroup,IPSSTitle,StandardLog
from core.utility import get_file_name

class RSNVolumeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RSNVolume
        fields = '__all__'

       
class RSNGroupSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['rsn_volume'] = {
            "id": obj.rsn_volume.id,
            "volume_no": obj.rsn_volume.volume_no,
            "volume_title": obj.rsn_volume.volume_title
        } if obj.rsn_volume else None
        return ret
    class Meta:
        model = RSNGroup
        fields = ['id', 'name', 'group_id']
        

class IPSSTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPSSTitle
        fields = '__all__'
 
class StandardSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        if obj.standard_type == "RSN":
            ret['volume'] = {
                "id": obj.rsn_volume.id,
                "name": obj.rsn_volume.volume_title,
                "volume_no": obj.rsn_volume.volume_no,
            } if obj.rsn_volume else None
            
            ret['group'] = { 
                "id": obj.group.id,
                "group_id": obj.group.group_id,
                "name": obj.group.name,
                "volume_no": obj.group.rsn_volume.volume_title,
            } if obj.group else None
            
            ret['no_of_sheet'] = obj.no_of_sheet
            
        elif obj.standard_type == "IPSS":
            ret['file_availability'] = obj.file_availability
            ret['title'] = {
                "id": obj.title.id,
                "title_id": obj.title.title_id,
                "title": obj.title.title
            } if obj.title else None
            
        else:
            ret['part_no'] = obj.part_no
            ret['section_no'] = obj.section_no
            ret['document_year'] = obj.document_year
            if obj.standard_type == "BIS":
                ret['division'] = obj.division
                ret['division_code'] = obj.division_code
                ret['committee_code'] = obj.committee_code
                ret['committee_title'] = obj.committee_title
        
        return ret
    class Meta:
        model = Standard
        fields = ['id', 'standard_no', 'standard_type', "description", "is_approved"]
     
class StandardArchiveSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        if obj.standard_type == "RSN":
            ret['volume'] = {
                "id": obj.rsn_volume.id,
                "name": obj.rsn_volume.volume_title,
                "volume_no": obj.rsn_volume.volume_no,
            } if obj.rsn_volume else None
            
            ret['group'] = { 
                "id": obj.group.id,
                "group_id": obj.group.group_id,
                "name": obj.group.name,
                "volume_no": obj.group.rsn_volume.volume_title,
            } if obj.group else None
            
            ret['title'] = {
                "id": obj.title.id,
                "title": obj.title.title
            }if obj.title else None
            
            ret['no_of_sheet'] = obj.no_of_sheet
            
        elif obj.standard_type == "IPSS":
            ret['file_availability'] = obj.file_availability
            ret['title'] = {
                "id": obj.title.id,
                "title": obj.title.title
            } if obj.title else None
            
        else:
            ret['part_no'] = obj.part_no
            ret['section_no'] = obj.section_no
            ret['document_year'] = obj.document_year
            if obj.standard_type == "BIS":
                ret['division'] = obj.division
                ret['division_code'] = obj.division_code
                ret['committee_code'] = obj.committee_code
                ret['committee_title'] = obj.committee_title
        
        return ret
    class Meta:
        model = Standard
        fields = ['id', 'standard_no', 'standard_type', "description", "is_approved", "archive_reason"]
    
class StandardDetailSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        if obj.standard_type == "RSN":
            ret['volume'] = {
                "id": obj.rsn_volume.id,
                "name": obj.rsn_volume.volume_title,
                "volume_no": obj.rsn_volume.volume_no,
            } if obj.rsn_volume else None
            
            ret['group'] = { 
                "id": obj.group.id,
                "group_id": obj.group.group_id,
                "name": obj.group.name,
                "volume_no": obj.group.rsn_volume.volume_title,
            } if obj.group else None
            
            ret['title'] = {
                "id": obj.title.id,
                "title": obj.title.title
            }if obj.title else None
            
            ret['no_of_sheet'] = obj.no_of_sheet
            
        elif obj.standard_type == "IPSS":
            ret['file_availability'] = obj.file_availability
            ret['title'] = {
                "id": obj.title.id,
                "title": obj.title.title
            } if obj.title else None
            
        else:
            ret['part_no'] = obj.part_no
            ret['section_no'] = obj.section_no
            ret['document_year'] = obj.document_year
            if obj.standard_type == "BIS":
                ret['division'] = obj.division
                ret['division_code'] = obj.division_code
                ret['committee_code'] = obj.committee_code
                ret['committee_title'] = obj.committee_title
        ret['file']= {
            "name":get_file_name(obj.upload_file.name),
            "size":obj.upload_file.size
            } if obj.upload_file else None       
        return ret
    class Meta:
        model = Standard
        fields = ['id', 'standard_no', 'standard_type', "description", "is_archive", "is_approved", "archive_reason"]
        
# search RSN Group 
class SearchRsnGroupSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['label'] = obj.name
        ret['value'] = obj.id
        return ret
    class Meta:
        model = RSNGroup
        fields = []
        read_only_fields = fields

# search RSN Volume      
class SearchRsnVolumeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['label'] = f"{obj.volume_no} ({obj.volume_title})"
        ret['value'] = obj.id
        return ret
    class Meta:
        model = RSNVolume
        fields = []
        read_only_fields = fields
        
# search IPSS Title 
class SearchIPSSTitleSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['label'] = obj.title
        ret['value'] = obj.id
        return ret
    class Meta:
        model = IPSSTitle
        fields = []
        read_only_fields = fields
        
        
class StandardLogSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['standard'] = {
            "id": obj.standard.id,
            "standard_no": obj.standard.standard_no,
            "standard_type": obj.standard.standard_type,
        } if obj.standard else None
        ret['user'] = {
            "id": obj.user.id,
            "full_name": obj.user.full_name,
            "personnel_number": obj.user.personnel_number,
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = StandardLog
        fields = ["id", "status", "message", "details"]
        read_only_fields = fields
        
        
class StandardLogExcelSerializer(serializers.ModelSerializer):
    def  to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['standard'] = f"{obj.standard.standard_type}-{obj.standard.standard_no}"
        ret['user'] = f"{obj.user.full_name} ({obj.user.personnel_number})"
        ret['message'] = obj.message
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        ret['details'] = obj.details
        return ret
    class Meta:
        model = StandardLog
        fields = []
        read_only_fields = fields

