from rest_framework import serializers
from django import forms
from .models import Order, WxUsers, OrderExport
from django.contrib.auth.models import User


class OrderSerializer(serializers.ModelSerializer):

    # nickname = serializers.ReadOnlyField(source='wx_users.nickname')  # 外键字段 只读

    class Meta:
        model = Order
        # exclude = ('id', )
        # fields = ('name', 'introduction', 'teacher', 'price')
        fields = '__all__'
        depth = 2


class WxSerializer(serializers.ModelSerializer):

    # department = serializers.ReadOnlyField(source='department.department_name')  # 外键字段 只读

    class Meta:
        model = WxUsers
        fields = '__all__'
        depth = 2  # 返回的深度，设置为几就表示有几层的关联外键信息


class OrderExportSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderExport
        fields = '__all__'
        depth = 1
