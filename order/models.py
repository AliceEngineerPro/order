# Create your models here.
from django.conf import settings
from django.db import models


class WxUsers(models.Model):
    wx_id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='微信ID')
    open_id = models.CharField(help_text="openid", verbose_name='openid', max_length=255)
    nickname = models.CharField(help_text="微信昵称", verbose_name='微信昵称', max_length=255)
    name = models.CharField(help_text="姓名", verbose_name='姓名', max_length=255, null=True)
    department = models.IntegerField(help_text="部门", verbose_name='部门', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "wx_users"  # 表名
        verbose_name = '微信用户信息'  # 这个verbose_name是在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        unique_together = ("open_id",)  # 唯一索引，联合索索引放入一个tuple

    # 调用时返回自身的属性，不然都是显示xx object
    # def __str__(self):
    #     return self.open_id


class Order(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    appointment_at = models.DateField(help_text='预约时间', verbose_name='预约时间', default=None)
    meal_type = models.SmallIntegerField(help_text="用餐时间，早餐：1；午餐：2：晚餐：3", verbose_name='用餐时间', default=None)
    wx_id = models.IntegerField(help_text="微信id", verbose_name='微信id', default=None)
    create_user = models.IntegerField(help_text="创建人（管理员）", verbose_name='创建人（管理员）', default=None, null=True)
    is_delete = models.SmallIntegerField(help_text="已取消：0否，1是", verbose_name='已取消', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "order_order"  # 表名
        verbose_name = '预约记录'  # 这个verbose_name是在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        # ordering = ('appointment_at',)  # 排序规则，默认主键
        unique_together = (("appointment_at", "meal_type", "wx_id"),)  # 唯一索引，联合索索引放入一个tuple
        # index_together = ()  # 普通索引

    # 调用时返回自身的属性，不然都是显示xx object
    # def __str__(self):
    #     return str(self.appointment_at)


class OrderExport(models.Model):
    export_id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='导出id')
    user_id = models.IntegerField(help_text="管理员id", verbose_name='管理员id', default=None)
    export_date = models.DateField(help_text="导出日期", verbose_name='导出日期')
    meal_type = models.IntegerField(help_text="用餐类型", verbose_name='用餐类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = "order_export"
        verbose_name = '导出记录'
        verbose_name_plural = verbose_name


class OrderOrder(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='id')
    appointment = models.DateField(verbose_name='预约时间')