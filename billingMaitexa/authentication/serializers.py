from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        exclude=['password']


class WebRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields = [
            'id','first_name', 'last_name', 'phone', 'phone_b', 'email',
            'gender', 'address_line1', 'address_line2', 'city',
            'state', 'zip_code', 'college', 'university', 'academic_year','project_title','internship','email_verified'
        ]