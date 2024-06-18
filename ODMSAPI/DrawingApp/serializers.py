from rest_framework import serializers
from DrawingApp.models import Drawing, DrawingFile, DrawingDescription, DrawingLog

class DrawingPendingListSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    
    def get_department(self, obj):
        return {"name": obj.department.name} if obj.department else None

    def get_unit(self, obj):
        return {"name": obj.unit.name} if obj.unit else None

    def get_volume(self, obj):
        if obj.sub_volume:
            return {
                "name": obj.sub_volume.name,
                "volume_name": obj.sub_volume.volume.name
            }
        return None
    def get_files(self, obj):
        return obj.files.select_related('drawing').all().values('id', 'file_name').order_by('file_name') or  []
    
    class Meta:
        model = Drawing
        fields = ["id", "drawing_type", "drawing_number", "no_of_sheet", "work_order_number", "is_layout", "default_description", "department", "unit", "volume", "files"]
        read_only_fields = fields

class DrawingListSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    
    def get_department(self, obj):
        return {"name": obj.department.name} if obj.department else None

    def get_unit(self, obj):
        return {"name": obj.unit.name} if obj.unit else None

    def get_volume(self, obj):
        if obj.sub_volume:
            return {
                "name": obj.sub_volume.name,
                "volume_name": obj.sub_volume.volume.name
            }
        return None
    def get_files(self, obj):
        return obj.files.select_related('drawing').all().values('id', 'file_name').order_by('file_name') or  []
    
    class Meta:
        model = Drawing
        fields = ["id", "drawing_type", "drawing_number", "revision_version", "work_order_number", "is_layout", "default_description", "department", "unit", "volume", "files"]
        read_only_fields = fields

class ArchiveDrawingListSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(ArchiveDrawingListSerializer, self).to_representation(obj)
        ret['department'] = {
                "id":obj.department.department_id,
                "name":obj.department.name, 
                "department_id":obj.department_id
            } if obj.department else None
        ret['unit'] = {
                "id":obj.unit.unit_id,
                "name":obj.unit.name, 
                "department_id":obj.unit_id
            } if obj.unit else None
        
        ret['volume'] = {
                "id":obj.sub_volume.id,
                "name":obj.sub_volume.name, 
                "sub_volume_no":obj.sub_volume.sub_volume_no,
                "volume_name":obj.sub_volume.volume.name
            } if obj.sub_volume else None
        
        return ret
    class Meta:
        model = Drawing
        fields = ["id", "drawing_type", "drawing_number", "revision_version", "archive_reason", "default_description"]
        read_only_fields = fields

class DrawingDetailSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(DrawingDetailSerializer, self).to_representation(obj)
        ret['department'] = {
                "id":obj.department.id,
                "name":obj.department.name, 
                "department_id":obj.department.department_id
            } if obj.department else None
        
        ret['unit'] = {
                "id":obj.unit.id,
                "name":obj.unit.name, 
                "unit_id":obj.unit.unit_id
            } if obj.unit else None
        
        ret['volume'] = {
                "id":obj.sub_volume.id,
                "name":obj.sub_volume.name, 
                "sub_volume_no":obj.sub_volume.sub_volume_no,
                "volume_name":obj.sub_volume.volume.name
            } if obj.sub_volume else None
        ret['date_of_registration'] = obj.date_of_registration
        return ret
    class Meta:
        model = Drawing
        fields = ["id", "drawing_type", "drawing_number", "no_of_sheet", "is_layout", "work_order_number",
                  "is_approved", "is_archive", "is_file_present", "is_dwg_file_present", "drawing_file_type",
                  "supplier_name", "client_number", "vendor_number", "package_number",
                  "revision_version", "drawing_size", "certification", "remarks", "archive_reason", "pdr_number", "letter_number", "fdr_approved_date"]
        read_only_fields = fields

class DrawingEditSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(DrawingEditSerializer, self).to_representation(obj)
        ret["description"] = obj.description.all().order_by('index').values("id", "description")
        ret['department'] = {
                "id":obj.department.id,
                "name":obj.department.name, 
                "department_id":obj.department.department_id
            } if obj.department else None
        
        ret['unit'] = {
                "id":obj.unit.id,
                "name":obj.unit.name, 
                "unit_id":obj.unit.unit_id
            } if obj.unit else None
        
        ret['volume'] = {
                "id":obj.sub_volume.id,
                "name":obj.sub_volume.name, 
                "sub_volume_no":obj.sub_volume.sub_volume_no,
                "volume_name":obj.sub_volume.volume.name
            } if obj.sub_volume else None
        ret['date_of_registration'] = obj.date_of_registration
        return ret
    class Meta:
        model = Drawing
        fields = ["id", "drawing_type", "drawing_number", "no_of_sheet", "is_layout", "work_order_number",
                  "is_approved", "is_archive", "is_file_present", "is_dwg_file_present", "drawing_file_type",
                  "supplier_name", "client_number", "vendor_number", "package_number",
                  "revision_version", "drawing_size", "certification", "remarks", "pdr_number", "letter_number", "fdr_approved_date"]
        read_only_fields = fields

class DrawingDescriptionSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(DrawingDescriptionSerializer, self).to_representation(obj)
        ret['drawing_file'] = DrawingFileSerializer(obj.drawing_file).data  if obj.drawing_file else None
        return ret
    class Meta:
        model = DrawingDescription
        fields = ["id", "index", "description"]
        read_only_fields = fields

class DrawingFileSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(DrawingFileSerializer, self).to_representation(obj)
        ret['file'] = obj.file.name
        ret['view_pdf_file'] = obj.view_pdf_file.name if obj.view_pdf_file else None
        ret['dwg_file'] = obj.dwg_file.name if obj.dwg_file else False
        return ret
    class Meta:
        model = DrawingFile
        fields = ["id", "file_name", "file_size"]
        read_only_fields = fields
        
        
class DrawingLogListSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(DrawingLogListSerializer, self).to_representation(obj)
        ret['drawing'] = {
            "id":obj.drawing.id,
            "drawing_number":obj.drawing.drawing_number,
            "drawing_type":obj.drawing.drawing_type,
        } if obj.drawing else None
        ret['user'] = {
            "id":obj.user.id,
            "full_name":obj.user.full_name,
            "personnel_number":obj.user.personnel_number,
        }
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        return ret
    class Meta:
        model = DrawingLog
        fields = ["id", "status", "message", "details"]
        read_only_fields = fields
        
        
class DrawingLogExcelListSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(DrawingLogExcelListSerializer, self).to_representation(obj)
        ret['drawing'] = f"{obj.drawing.drawing_type}-{obj.drawing.drawing_number}" if obj.drawing else None
        ret['user'] = f"{obj.user.full_name} ({obj.user.personnel_number})"
        ret["status"] = obj.status
        ret['message'] = obj.message
        ret['action_time'] = obj.action_time.strftime("%d %b %Y %I:%M %p")
        ret['details'] = obj.details
        return ret
    class Meta:
        model = DrawingLog
        fields = []
        read_only_fields = fields


class SearchDrawingSerializer(serializers.Serializer):
    id = serializers.CharField()
    drawing_type = serializers.CharField()
    drawing_number = serializers.CharField()
    
    def to_representation(self, obj):
        ret = super(SearchDrawingSerializer, self).to_representation(obj)
        ret['label'] = f'{obj["drawing_type"]}-{obj["drawing_number"]}'
        ret['value'] = obj['id']
        return ret