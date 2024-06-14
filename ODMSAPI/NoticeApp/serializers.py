from rest_framework import serializers
from .models import Notice,Slider, NewUserRequest



class NoticeSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Notice
        fields = ['id', 'notice']
        

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = ['id', 'media', 'is_published']

class NewUserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUserRequest
        fields = ["id", "full_name", "email", "phone_number", "personnel_number", "designation", "department", "created_at"]
        read_only_fields = fields