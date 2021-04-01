from order import models
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication


class Auth(BaseAuthentication):
    """
    微信认证
    """
    def authenticate(self, request):
        openid = request.META.get("HTTP_OPENID")  # 请求的openid
        res = models.WxUsers.objects.filter(open_id=openid).first()  # 用户信息
        if res:
            return res, None  # return返回的内容分别添加到request.user和request.auth中
        else:
            raise exceptions.APIException('您还没有登录!')
