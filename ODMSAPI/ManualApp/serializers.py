from rest_framework import serializers

from core.utility import get_file_name
from . models import Manual, ManualLog


class ManualSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        if obj.manual_type in ["MANUALS","TENDER DOCUMENT","TECHNICAL CALCULATION","TECHNICAL SPECIFICATION", "TECHNICAL REPORT", "PROJECT SUBMITTED DRAWINGS"]:
            ret['department'] = {
                "id": obj.department.id,
                "name": obj.department.name,
                "department_id": obj.department.department_id,
            }if obj.department else None
            
            if obj.manual_type == "MANUALS":
                ret['package_no'] = obj.package_no
                ret['letter_no'] = obj.letter_no
                ret['registration_date'] = obj.registration_date
            
            if obj.manual_type in ["MANUALS","TENDER DOCUMENT", "PROJECT SUBMITTED DRAWINGS"]:
                ret['unit'] = {
                    "id": obj.unit.id,
                    "name": obj.unit.name,
                    "unit_id": obj.unit.unit_id,
                }if obj.unit else None
            
        if obj.manual_type in ["MANUALS", "TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION","TECHNICAL REPORT", "PROJECT REPORT"]:
            ret['supplier'] = obj.supplier
            if obj.manual_type in ["MANUALS", "PROJECT REPORT"]:
                ret['remarks'] = obj.remarks
            if obj.manual_type == "PROJECT REPORT":
                ret['capacity'] = obj.capacity
                ret['year'] = obj.year
                
        if obj.manual_type in ["REFERENCE BOOK", "CATALOUGE"]:
            ret['source'] = obj.source
            if obj.manual_type == "REFERENCE BOOK":
                ret['editor'] = obj.editor
                ret['author'] = obj.author
        
        if obj.manual_type == "PROJECT SUBMITTED DRAWINGS":
            ret['title'] = obj.title

        ret['is_file'] =  True if obj.upload_file else False
        return ret        
    class Meta:
        model = Manual
        fields = ['id','manual_type', 'manual_no','description', 'is_approved']
        

class ManualArchiveSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        if obj.manual_type in ["MANUALS","TENDER DOCUMENT","TECHNICAL CALCULATION","TECHNICAL SPECIFICATION", "TECHNICAL REPORT"]:
            ret['department'] = {
                "id": obj.department.id,
                "name": obj.department.name,
                "department_id": obj.department.department_id,
            }if obj.department else None
            
            if obj.manual_type == "MANUALS":
                ret['package_no'] = obj.package_no
                ret['letter_no'] = obj.letter_no
                ret['registration_date'] = obj.registration_date
            
            if obj.manual_type in ["MANUALS","TENDER DOCUMENT"]:
                ret['unit'] = {
                    "id": obj.unit.id,
                    "name": obj.unit.name,
                    "unit_id": obj.unit.unit_id,
                }if obj.unit else None
            
        if obj.manual_type in ["MANUALS", "TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION","TECHNICAL REPORT", "PROJECT REPORT"]:
            ret['supplier'] = obj.supplier
            if obj.manual_type in ["MANUALS", "PROJECT REPORT"]:
                ret['remarks'] = obj.remarks
            if obj.manual_type == "PROJECT REPORT":
                ret['capacity'] = obj.capacity
                ret['year'] = obj.year
                
        if obj.manual_type in ["REFERENCE BOOK", "CATALOUGE"]:
            ret['source'] = obj.source
            if obj.manual_type == "REFERENCE BOOK":
                ret['editor'] = obj.editor
                ret['author'] = obj.author
        return ret        
    class Meta:
        model = Manual
        fields = ['id','manual_type', 'manual_no','description', 'is_approved', 'archive_reason']


class ManualDetailSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        if obj.manual_type in ["MANUALS","TENDER DOCUMENT","TECHNICAL CALCULATION","TECHNICAL SPECIFICATION", "TECHNICAL REPORT", "PROJECT SUBMITTED DRAWINGS"]:
            ret['department'] = {
                "id": obj.department.id,
                "name": obj.department.name,
                "department_id": obj.department.department_id,
            }if obj.department else None
            
            if obj.manual_type == "MANUALS":
                ret['package_no'] = obj.package_no
                ret['letter_no'] = obj.letter_no
                ret['registration_date'] = obj.registration_date
            
            if obj.manual_type in ["MANUALS","TENDER DOCUMENT", "PROJECT SUBMITTED DRAWINGS"]:
                ret['unit'] = {
                    "id": obj.unit.id,
                    "name": obj.unit.name,
                    "unit_id": obj.unit.unit_id,
                }if obj.unit else None
            
        if obj.manual_type in ["MANUALS", "TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION","TECHNICAL REPORT", "PROJECT REPORT"]:
            ret['supplier'] = obj.supplier
            if obj.manual_type in ["MANUALS", "PROJECT REPORT"]:
                ret['remarks'] = obj.remarks
            if obj.manual_type == "PROJECT REPORT":
                ret['capacity'] = obj.capacity
                ret['year'] = obj.year
                
        if obj.manual_type in ["REFERENCE BOOK", "CATALOUGE"]:
            ret['source'] = obj.source
            if obj.manual_type == "REFERENCE BOOK":
                ret['editor'] = obj.editor
                ret['author'] = obj.author

        if obj.manual_type == "PROJECT SUBMITTED DRAWINGS":
            ret['title'] = obj.title
            ret['file_type'] = obj.file_type
            ret['dwg_zip_file']= {
            "name":get_file_name(obj.dwg_zip_file.name),
            "size":obj.dwg_zip_file.size
            } if obj.dwg_zip_file else None
        
        ret['file']= {
            "name":get_file_name(obj.upload_file.name),
            "size":obj.upload_file.size
            } if obj.upload_file else None
        return ret        
    class Meta:
        model = Manual
        fields = ['id','manual_type', 'manual_no','description', 'is_archive', 'is_approved', 'archive_reason',]
        
        
class ManualLogSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['manual'] = {
            "id": obj.manual.id,
            "manual_no": obj.manual.manual_no,
            "manual_type": obj.manual.manual_type,
        } if obj.manual else None
        ret['user'] = {
            "id": obj.user.id,
            "full_name": obj.user.full_name,
            "personnel_number": obj.user.personnel_number
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = ManualLog
        fields = ["id", "status", "message", "details"]
        read_only_fields = fields
        
        
class ManualLogExcelSerializer(serializers.ModelSerializer):
    def  to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['manual'] = f"{obj.manual.manual_type}-{obj.manual.manual_no}"
        ret['user'] = f"{obj.user.full_name} ({obj.user.personnel_number})"
        ret['message'] = obj.message
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        ret['details'] = obj.details
        return ret    
    class Meta:
        model = ManualLog
        fields = []
        read_only_fields = fields