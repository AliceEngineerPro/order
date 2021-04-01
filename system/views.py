import logging

from django.shortcuts import render

# Create your views here.

from .booking_status import BookingStatus
from .models import SysDepartment, SysWxUsers
from .serializers import SysDepartmentSerializer, SysWxUserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny


class DepartmentList(APIView):

    permission_classes = (AllowAny, )  # 允许所有访问

    def get(self, request):
        queryset = SysDepartment.objects.all()
        list_all = SysDepartmentSerializer(instance=queryset, many=True)
        return Response(list_all.data)


class WxUsersList(APIView):

    permission_classes = (AllowAny, )  # 允许所有访问

    def get(self, request):
        if 'department' in request.GET:
            pk = request.GET.get('department')
            queryset = SysWxUsers.objects.filter(department=pk)
            list_all = SysWxUserSerializer(instance=queryset, many=True)
            return Response(list_all.data)
        obj = SysWxUsers.objects.all()
        s = SysWxUserSerializer(instance=obj, many=True)
        return Response(s.data)


class Booking(APIView):

    permission_classes = (AllowAny, )  # 允许所有访问

    """
    查询最近三天的订餐是否允许预约
    预约状态：
    0：允许预约/修改
    1：不允许预约/修改，但允许管理员预约/修改
    2： 已超时，所有人不可修改
    """
    def get(self, request):
        if 'appointment_at' in request.GET:
            return Response(BookingStatus.booking_status(request.GET['appointment_at']))
        return Response(BookingStatus.booking_status())
