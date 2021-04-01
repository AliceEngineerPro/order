from rest_framework.serializers import Serializer
from .models import SysDepartment, SysWxUsers
from rest_framework import serializers


class SysDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysDepartment
        fields = 'department_id', 'department_name'
        depth = 2


class SysWxUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysWxUsers
        fields = 'wx_id', 'name', 'department'
        depth = 2
