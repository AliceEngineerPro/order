from django.db import models

# Create your models here.

from django.conf import settings


class SysDepartment(models.Model):
    department_id = models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name="id",
                                     help_text="部门id")
    department_name = models.CharField(max_length=255, verbose_name='部门', help_text='部门')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        managed = False
        db_table = "sys_department"
        verbose_name = '部门'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.department_name


class SysWxUsers(models.Model):
    wx_id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='微信ID')
    open_id = models.CharField(help_text="openid", verbose_name='openid', max_length=255)
    nickname = models.CharField(help_text="微信昵称", verbose_name='微信昵称', max_length=255)
    name = models.CharField(help_text="姓名", verbose_name='姓名', max_length=255, null=True)
    department = models.IntegerField(help_text="部门", verbose_name='部门', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        managed = False
        db_table = "wx_users"
        verbose_name = '员工姓名'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
