from rest_framework import serializers

from core.utility import get_file_name
from .models import *


class SirSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['department'] = {
            "id": obj.department.id,
            "name": obj.department.name,
            "department_id": obj.department.department_id,
        }if obj.department else None
        
        ret['unit'] = {
            "id": obj.unit.id,
            "name": obj.unit.name,
            "unit_id": obj.unit.unit_id,
        }if obj.unit else None
        
        ret['attachment']= {
            "name":get_file_name(obj.attachment.path),
            "size":obj.attachment.size
            } if obj.attachment else None
        
        return ret
    class Meta:
        model = SIR
        fields = ['id', 'sir_number', 'year_of_inspection', 'compliance', 'description', 'is_approved', 'is_archive', 'archive_reason', 'created_at']
        
class SIRLogSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['sir'] = {
            "id": obj.sir.id,
            "sir_number": obj.sir.sir_number,
        } if obj.sir else None
        ret['user'] = {
            "id": obj.user.id,
            "full_name": obj.user.full_name,
            "personnel_number": obj.user.personnel_number
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = SIRLog
        fields = ["id", "status", "message", "details"]
        
class SIRLogExcelSerializer(serializers.ModelSerializer):
    def  to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['sir'] = f"{obj.sir.sir_number if obj.sir else None}"
        ret['user'] = f"{obj.user.full_name} ({obj.user.personnel_number})"
        ret['message'] = obj.message
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        ret['details'] = obj.details
        return ret 
    class Meta:
        model = SIRLog
        fields = []
        read_only_fields = fields



class StabilityCertificationSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['department'] = {
            "id": obj.department.id,
            "name": obj.department.name,
            "department_id": obj.department.department_id,
        }if obj.department else None
        
        ret['unit'] = {
            "id": obj.unit.id,
            "name": obj.unit.name,
            "unit_id": obj.unit.unit_id,
        }if obj.unit else None
        
        ret['attachment']= {
            "name":get_file_name(obj.attachment.name),
            "size":obj.attachment.size
            } if obj.attachment else None
        
        return ret
    class Meta:
        model = StabilityCertification
        fields = ['id', 'certificate_number', 'created_at', 'is_approved', 'is_archive', 'archive_reason', 'created_at']

class StabilityCertificationLogSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['stability_certification'] = {
            "id": obj.stability_certification.id,
            "certificate_number": obj.stability_certification.certificate_number,
        } if obj.stability_certification else None
        ret['user'] = {
            "id": obj.user.id,
            "full_name": obj.user.full_name,
            "personnel_number": obj.user.personnel_number
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = StabilityCertificationLog
        fields = ["id", "status", "message", "details"]

class StabilityCertificationLogExcelSerializer(serializers.ModelSerializer):
    def  to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['stability_certification'] = f"{obj.stability_certification.certificate_number if obj.stability_certification else None}"
        ret['user'] = f"{obj.user.full_name} ({obj.user.personnel_number})"
        ret['message'] = obj.message
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        ret['details'] = obj.details
        return ret 
    class Meta:
        model = StabilityCertificationLog
        fields = []
        read_only_fields = fields


     
class ComplianceSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['department'] = {
            "id": obj.department.id,
            "name": obj.department.name,
            "department_id": obj.department.department_id,
        }if obj.department else None
        
        ret['unit'] = {
            "id": obj.unit.id,
            "name": obj.unit.name,
            "unit_id": obj.unit.unit_id,
        }if obj.unit else None
        
        ret['attachment']= {
            "name":get_file_name(obj.attachment.name),
            "size":obj.attachment.size
            } if obj.attachment else None
        
        return ret
    class Meta:
        model = Compliance
        fields = ['id', 'reference_number', 'is_approved', 'is_archive', 'archive_reason', 'created_at']

class ComplianceLogSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['compliance'] = {
            "id": obj.compliance.id,
            "reference_number": obj.compliance.reference_number,
        } if obj.compliance else None
        ret['user'] = {
            "id": obj.user.id,
            "full_name": obj.user.full_name,
            "personnel_number": obj.user.personnel_number
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = ComplianceLog
        fields = ["id", "status", "message", "details"]    
        
class ComplianceLogExcelSerializer(serializers.ModelSerializer):
    def  to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['compliance'] = f"{obj.compliance.reference_number if obj.compliance else None}"
        ret['user'] = f"{obj.user.full_name} ({obj.user.personnel_number})"
        ret['message'] = obj.message
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        ret['details'] = obj.details
        return ret 
    class Meta:
        model = ComplianceLog
        fields = []
        read_only_fields = fields     

# document serializer
        
class DocumentSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['attachment']= {
            "name":get_file_name(obj.attachment.name),
            "size":obj.attachment.size
            } if obj.attachment else None
        
        return ret
    class Meta:
        model = Document
        fields = ['id', 'document_number', "description", 'is_archive', 'archive_reason', 'created_at']

class DocumentLogSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['document'] = {
            "id": obj.document.id,
            "document_number": obj.document.document_number,
        } if obj.document else None
        ret['user'] = {
            "id": obj.user.id,
            "full_name": obj.user.full_name,
            "personnel_number": obj.user.personnel_number
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = ComplianceLog
        fields = ["id", "status", "message", "details"]    
        
class DocumentLogExcelSerializer(serializers.ModelSerializer):
    def  to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['document'] = f"{obj.document.document_number if obj.document else None}"
        ret['user'] = f"{obj.user.full_name} ({obj.user.personnel_number})"
        ret['message'] = obj.message
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        ret['details'] = obj.details
        return ret 
    class Meta:
        model = ComplianceLog
        fields = []
        read_only_fields = fields     
        
        
        
        
        
        
