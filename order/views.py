# encoding=utf8

import datetime

import pymysql
import xlwt
from django.http import FileResponse
from django.shortcuts import render

# Create your views here.
from django.utils.encoding import escape_uri_path
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from system.booking_status import BookingStatus
from .models import Order, WxUsers, OrderExport
from .serializers import OrderSerializer, WxSerializer, OrderExportSerializer
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import viewsets
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerReadOnly
from django.db import transaction, IntegrityError
from ordering.database import Database
from system.booking_status import BookingStatus
import datetime
import os


@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # Django的信号机制
def generate_token(sender, instance=None, created=False, **kwargs):
    """
    创建用户时自动生成Token
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        Token.objects.create(user=instance)


class OrderList(APIView):
    def get(self, request):
        sql = ""
        time = datetime.datetime.now().strftime("%Y-%m-%d")
        wx_id = request.GET.get('wx_id')
        department = request.GET.get('department')
        appointment_at = request.GET.get('appointment_at')
        if appointment_at == None:
            appointment_at = datetime.datetime.now().strftime("%Y-%m-%d")
        sqlList = [appointment_at]
        if wx_id != None:
            sql += " and oo.wx_id = %s "
            sqlList.append(wx_id)
        if department != None:
            sql += " and sd.department_id = %s "
            sqlList.append(department)
        cursor = Database.cursor()
        sql1 = "SELECT oo.id AS id, oo.appointment_at, oo.wx_id AS wx_id,wu.name,sd.department_name AS `department`, oo.meal_type AS meal_type FROM order_order AS oo LEFT JOIN wx_users AS wu ON  oo.wx_id = wu.wx_id  LEFT JOIN sys_department AS sd ON wu.department = sd.department_id LEFT JOIN auth_user AS au ON oo.create_user = au.id WHERE oo.is_delete = 0 and oo.appointment_at = %s " + sql + " GROUP BY oo.wx_id "
        cursor.execute(sql1, sqlList)
        row = cursor.fetchall()
        data = []
        dict = {}
        for r in row:
            list = [None, None, None]
            wx_id = r.get('wx_id')
            if appointment_at == None:
                wxIds = Order.objects.filter(wx_id=wx_id, appointment_at=time, is_delete=0)
            else:
                wxIds = Order.objects.filter(wx_id=wx_id, appointment_at=appointment_at, is_delete=0)
            orders = OrderSerializer(instance=wxIds, many=True)
            for id in orders.data:
                order = id.get('meal_type')
                meal_id = id.get('id')
                if order == 1:
                    list[0] = meal_id
                elif order == 2:
                    list[1] = meal_id
                elif order == 3:
                    list[2] = meal_id
            str = {"appointment_at": r.get('appointment_at'), "wx_id": r.get('wx_id'), "name": r.get('name'),
                   "department": r.get('department'), "order": list}
            data.append(str)
        dict.setdefault("msg", "查询成功")
        dict.setdefault("code", 0)
        dict.setdefault("data", data)
        return Response(dict)

    def post(self, request):
        meal_type = request.data['meal_type']

        data = request.data
        data['create_user'] = request.user.id

        # 查询指定日期的预约情况
        booking = BookingStatus.booking_status(data['appointment_at'])
        msg = '预约成功'
        # 验证当前餐是否允许预约
        if booking[meal_type - 1] == 1:
            msg += ',请将当前餐型重新导出'
        if booking[meal_type - 1] == 2:
            return Response(data={'msg': '新增预约失败,当前订餐已截止', 'code': -1})

        s = OrderSerializer(data=data)
        # 验证是否可以新增
        if s.is_valid():
            s.save()
            return Response(data={'msg': msg, 'code': 0})
        else:
            # 验重:查询这条数据如果是否已经存在
            order = Order.objects.filter(appointment_at=data['appointment_at'],
                                         wx_id=data['wx_id'], meal_type=data['meal_type']).first()
            if order:  # 如果存在这条预约
                if order.is_delete:  # 如果已删除，恢复这条数据
                    obj = Order.objects.get(pk=order.id)  # 找到这条订单记录
                    s = OrderSerializer(instance=obj, data={'is_delete': 0}, partial=True)  # 序列化这条订单实例
                    if s.is_valid():  # 验证格式
                        s.save()
                        return Response(data={'msg': msg, 'code': 0})
                    else:
                        return Response(data={'msg': '预约失败', 'code': -1})
                else:
                    return Response(data={'msg': '预约失败，此餐此前已预约', 'code': -1})
            else:
                return Response(data={'msg': '预约失败', 'code': -1})

    def patch(self, request):
        id = request.data['id']
        obj = Order.objects.get(pk=id)
        msg = "修改订餐信息成功"
        #查询指定日期的预约情况
        list = BookingStatus.booking_status(obj.appointment_at)
        #得到用户所定餐型
        meal_type = obj.meal_type
        for index, value in enumerate(list):
            #遍历判断能否修改数据
            if meal_type == index + 1 and value == 2:
                return Response(data={"msg":"已过取消时间,修改失败", "code":-1})
            if meal_type == index + 1 and value == 1:
                msg += ",请将当前餐型重新导出"
            if meal_type == index + 1 and value == 0:
                msg = "修改订餐信息成功"
        #更新到数据库
        s = OrderSerializer(instance=obj, data=request.data, partial=True)
        if s.is_valid():
            s.save(is_delete=1)
            return Response(data={"msg":msg, "code":0})
        return Response(data={"msg":"服务器异常,修改失败", "code":-1})

class OrderExportList(APIView):

    def post(self, request):
        """
        :param request:
        :return:
        """
        appointment_at = request.data['appointment_at']
        meal_types = request.data['meal_types']
        cursor = Database.cursor()

        excelname = str(appointment_at) + '.xls'
        filename = 'static/resources/' + excelname

        # 如果已经存在，删除这个文件
        if os.path.exists(filename):
            os.remove(filename)

        # excel文件
        workbook = xlwt.Workbook(encoding='utf-8')
        meals = ['早', '午', '晚']

        success = False

        for meal_type in meal_types:
            sql = "SELECT oo.id AS '预约编号', wu.`name` AS '姓名', sd.department_name AS '所属部门', oo.appointment_at AS '用餐日期', CASE WHEN oo.meal_type = 1 THEN '早餐' WHEN oo.meal_type = 2 THEN '午餐' WHEN oo.meal_type = 3 THEN '晚餐' END AS '用餐类型', wu.nickname AS '微信昵称', oo.updated_at AS '预约时间' FROM order_order AS oo LEFT JOIN wx_users AS wu ON oo.wx_id = wu.wx_id LEFT JOIN sys_department AS sd ON wu.department = sd.department_id WHERE oo.is_delete = 0 AND oo.appointment_at = %s AND oo.meal_type = %s"
            cursor.execute(sql, [appointment_at, meal_type])
            row = cursor.fetchall()

            if len(row) == 0:
                continue
            else:
                success = True

            # 增加当前餐的sheet
            worksheet = workbook.add_sheet(str(meals[int(meal_type) - 1]) + '餐')
            # 增加表头
            header = list(row[0].keys())
            for index, value in enumerate(header):
                worksheet.write(0, index, label=value)

            worksheet.col(1).width = 3000  # 姓名
            worksheet.col(2).width = 4000  # 所属部门
            worksheet.col(3).width = 3000  # 用餐日期
            # worksheet.col(4).width = 5000  # 用餐类型
            worksheet.col(5).width = 3000  # 微信昵称
            worksheet.col(6).width = 5000  # 预约时间
            # 表内容
            for index, value in enumerate(row):
                for idx, v in enumerate(list(value.values())):
                    if str(type(v)) == '<class \'datetime.date\'>':
                        style = xlwt.XFStyle()
                        style.num_format_str = 'YY-MM-DD'
                        worksheet.write((index + 1), idx, v, style)
                    elif str(type(v)) == '<class \'datetime.datetime\'>':
                        # 日期类型处理
                        style = xlwt.XFStyle()
                        style.num_format_str = 'YY-MM-DD hh:mm:ss'
                        worksheet.write((index + 1), idx, v, style)
                    else:
                        worksheet.write((index+1), idx, label=v)

            # 增加导出记录
            s = OrderExportSerializer(data={'user_id': request.user.id, 'export_date': appointment_at, 'meal_type': meal_type})
            if s.is_valid():
                s.save()

        if not success:
            return Response({'msg': '导出失败，指定餐型没有数据', 'code': -1})

        workbook.save(filename)

        file = open(filename, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(str(appointment_at) + '订餐记录.xls'))

        return response


class getTotal(APIView):
    def get(self, request):
        time = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor = Database.cursor()
        sql = "SELECT COUNT(DISTINCT oo.wx_id) AS value, sd.department_name AS name FROM wx_users wu, order_order oo, sys_department sd WHERE wu.wx_id = oo.wx_id AND sd.department_id = wu.department AND oo.is_delete = 0 AND oo.appointment_at = %s GROUP BY sd.department_id "
        cursor.execute(sql, [time])
        row = cursor.fetchall()
        return Response(row, )
