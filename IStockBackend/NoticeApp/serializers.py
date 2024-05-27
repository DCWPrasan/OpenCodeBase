from rest_framework import serializers
from .models import Notice,Slider, NewUserRequest
from datetime import datetime



class NoticeSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super().to_representation(obj)
        ret['created_at'] = datetime.strftime(obj.created_at, "%d %b %Y")
        return ret 
    class Meta:
        model = Notice
        fields = ['id', 'title', 'description', 'is_published']
        

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = ['id', 'media', 'is_published']

class NewUserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUserRequest
        fields = ["id", "full_name", "email", "phone_number", "personnel_number", "designation", "department", "cost_code_department", "created_at"]
        read_only_fields = fields