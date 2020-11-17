from django.urls import path

from cart import views

urlpatterns = [
    path('add/', views.CartAPIView.as_view({
        'post': 'add_to_cart', 'get': 'show_car', 'patch': 'change_select',
        'delete': 'delete_course','put': 'change_expire',
    })),
    path('checked/',views.CarAllCheckedViewset.as_view({
        'patch': 'checked_all','delete':'delete_all',
        'get': 'get_order_data',
    })),

]
