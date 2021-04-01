from django.urls import path
from wx import views

urlpatterns = [
    # Function Based View
    # path("wx/login", views.wx_login, name="wx_login"),

    # Class Based View
    path("login", views.UserLogin.as_view(), name="wx-login"),
    path("user", views.User.as_view(), name="wx-user"),
    path("wx", views.WxUser.as_view(), name="wx-wx-user"),
    path("order", views.Order.as_view(), name="wx-wx-order")
]
