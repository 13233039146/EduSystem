from django.urls import path

from cart import views

urlpatterns = [
    path('add/', views.CartAPIView.as_view({
        'post': 'add_to_cart', 'get': 'show_car', 'patch': 'change_select',
        'delete': 'delete_course',
    })),

]
