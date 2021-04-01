from django.urls import path
from system import views

urlpatterns = [
    path('department', views.DepartmentList.as_view(), name='sys-department'),
    path('wx', views.WxUsersList.as_view(), name="sys-user"),
    path('booking', views.Booking.as_view(), name="sys-booking"),
]
