import pymysql
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from wechatpy import WeChatClient
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from wechatpy.session import SessionStorage
from wechatpy.client.api import WeChatWxa
from order import models
from system.booking_status import BookingStatus
from .auth import Auth
from order.serializers import WxSerializer, OrderSerializer
from system.models import SysDepartment
from ordering.database import Database


class CustomStorage(SessionStorage):

    def __init__(self, *args, **kwargs):
        pass

    def get(self, key, default=None):
        pass

    def set(self, key, value, ttl=None):
        pass

    def delete(self, key):
        pass


class UserLogin(APIView):
    permission_classes = (AllowAny,)  # 允许所有访问

    def post(self, request):
        appid = 'wx913f229778bb0119'
        secret = '0e927f55e8c7f21b566b70881d8c130e'
        client = WeChatClient(appid, secret, session=CustomStorage())
        # user = client.user.get('openid')
        wxa = WeChatWxa(client)
        token = wxa.code_to_session(js_code=request.data['code'])

        return Response(data={'token': token}, status=status.HTTP_200_OK)


class User(APIView):
    # authentication_classes = [Auth, ]  # 要求header保存了openid
    permission_classes = (AllowAny,)  # 允许所有访问

    @staticmethod
    def get_object(pk):
        try:
            return models.WxUsers.objects.get(pk=pk)
        except models.WxUsers.DoesNotExist:
            return

    def post(self, request):
        openid = request.META.get("HTTP_OPENID")
        if openid is None:
            return Response(data={"msg": "没有用户信息"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 查询数据库是否有这条数据
        res = models.WxUsers.objects.filter(open_id=openid).first()

        # 如果没有用户信息新建一条，如果有用户信息更新用户名
        if res is None:
            s = WxSerializer(data={"open_id": openid, "nickname": request.data['nickName']})
            # 校验
            if s.is_valid():
                s.save()
                return Response(data={'msg': '新建用户成功'}, status=status.HTTP_200_OK)
        else:
            obj = self.get_object(pk=res.wx_id)
            if not obj:
                return Response(data={"msg": "没有此用户信息"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            s = WxSerializer(instance=obj, data={"nickname": request.data['nickName']}, partial=True)
            if s.is_valid():
                s.save()
                return Response(data={'msg': '用户信息更新成功'}, status=status.HTTP_200_OK)
            return Response(s.errors, status.HTTP_400_BAD_REQUEST)

        return Response(data={'token': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WxUser(APIView):
    permission_classes = (AllowAny,)  # 允许所有访问
    authentication_classes = (Auth,)  # 要求header保存了openid,否则进行拦截

    @staticmethod
    def get_object(pk):
        try:
            return models.WxUsers.objects.get(pk=pk)
        except models.WxUsers.DoesNotExist:
            return

    def get(self, request):
        """
        查询当前用户姓名和公司
        :param request:
        :return:
        """
        print(request.user)
        print(request.user.wx_id)
        department = '未选择公司'

        # 查询单位及单位名
        if request.user.department:
            department = SysDepartment.objects.get(department_id=request.user.department).department_name

        return Response(data={
            'name': request.user.name,
            'department_id': request.user.department,
            'department': department
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        修改当前用户
        :param request:
        :return:
        """
        # 验证是否已经填写了name和department
        if request.data['name'] is None or not isinstance(request.data['department'], int):
            return Response(data={'msg': '修改失败，格式错误', 'code': -1})

        obj = self.get_object(pk=request.user.wx_id)
        s = WxSerializer(instance=obj, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(data={'msg': '修改成功', 'code': 0})
        return Response(data={'msg': '修改失败，格式错误', 'code': -1})


class Order(APIView):
    permission_classes = (AllowAny,)  # 允许所有访问
    authentication_classes = (Auth,)  # 要求header保存了openid,否则进行拦截

    # @staticmethod
    # def get_object(pk):
    #     try:
    #         return models.Order.objects.get(pk=pk)
    #     except models.WxUsers.DoesNotExist:
    #         return

    """查询我的预约"""
    def get(self, request):
        cursor = Database.cursor()
        sql = 'SELECT appointment_at, meal_type, id FROM order_order WHERE wx_id = %s AND is_delete = 0 ORDER BY appointment_at DESC'
        cursor.execute(sql, [request.user.wx_id])
        row = cursor.fetchall()
        result = {}
        for item in row:
            appointment_at = str(item['appointment_at'])
            if appointment_at in result:
                result[appointment_at]['meals'][item['meal_type'] - 1] = item['id']
            else:
                meals = [None, None, None]
                meals[item['meal_type'] - 1] = item['id']
                result[appointment_at] = {
                    'appointment_at': appointment_at,
                    'meals': meals
                }
        return Response(list(result.values()))

    """预约"""
    def post(self, request):
        data = request.data
        booking = BookingStatus.booking_status(data['appointment_at'])
        if booking[data['meal_type'] - 1] > 0:
            return Response({'msg': '预约失败,预约已截止', 'code': -1})

        data['wx_id'] = request.user.wx_id
        s = OrderSerializer(data=data)
        if s.is_valid():
            s.save()
            return Response({'msg': '预约成功', 'code': 0})
        else:
            # 判断是否已经存在了这条数据
            order = models.Order.objects.filter(appointment_at=data['appointment_at'],
                                                wx_id=data['wx_id'], meal_type=data['meal_type']).first()
            if order:  # 如果存在这条预约
                if order.is_delete:  # 如果已删除，恢复这条数据
                    obj = models.Order.objects.get(pk=order.id)  # 找到这条订单记录
                    s = OrderSerializer(instance=obj, data={'is_delete': 0}, partial=True)  # 序列化这条订单实例
                    if s.is_valid():  # 验证格式
                        s.save()
                        return Response({'msg': '预约成功', 'code': 0})
                    else:
                        return Response({'msg': '预约失败', 'code': -1})
                else:
                    return Response({'msg': '预约失败，此餐已预约，不能重复预约', 'code': -1})
            else:
                return Response({'msg': '预约失败', 'code': -1})

    def put(self, request):
        order = models.Order.objects.filter(pk=request.data['id']).first()

        # 检查这个预约是不是自己
        if order.wx_id != request.user.wx_id:
            return Response({"msg": "您不可以取消其他人的预约", "code": -1})

        # todo 判断是否已经截止

        s = OrderSerializer(instance=order, data={'is_delete': 1}, partial=True)  # 序列化这条订单实例
        if s.is_valid():
            s.save()
        return Response({'msg': '取消预约成功', 'code': 0})
