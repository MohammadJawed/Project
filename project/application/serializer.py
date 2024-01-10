from rest_framework import serializers
from .models import CustomUser,employeeData

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name']

class Employee_CountSerializer(serializers.Serializer):
    department__name = serializers.CharField()
    user_count = serializers.IntegerField()