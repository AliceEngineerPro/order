from django.urls import path, include
from order import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)  # trailing_slash=False删除url末位的斜杠

urlpatterns = [
    # viewsets
    # path("", include(router.urls)),

    # # Function Based View
    # path("fbv/list/", views.Order_list, name="fbv-list"),
    # path("fbv/detail/<int:pk>", views.Order_detail, name="fbv-detail"),
    #
    # Class Based View
    # path("cbv/list/", views.OrderList.as_view(), name="cbv-list"),
    # path("cbv/detail/<int:pk>", views.OrderDetail.as_view(), name="cbv-detail"),
    #
    # # Generic Class Based View
    # path("gcbv/list/", views.GOrderList.as_view(), name="gcbv-list"),
    # path("detail/<int:pk>", views.GWxDetail.as_view(), name="gcbv-detail"),

    # DRF viewsets
    # path("viewsets/", views.OrderViewSet.as_view({
    #     "get": "list",
    #     "post": "create"
    # }), name="viewsets-list"),
    # path("viewsets/<int:pk>", views.OrderViewSet.as_view({
    #     "get": "retrieve",
    #     "put": "update",
    #     "patch": "partial_update",  # 部分更新
    #     "delete": "destroy",
    # }), name="viewsets-detail"),

    # path("cbv/list/", views.OrderList.as_view(), name="cbv-list"),
    path('order',views.OrderList.as_view(),name='order_list'),
    path("export", views.OrderExportList.as_view(), name="cbv-list"),
    path("total", views.getTotal.as_view(), name="getTotal"),

]
