from django.urls import path

from order.views import OrderCreateAPIView


urlpatterns = [
    path('pay_money/', OrderCreateAPIView.as_view()),

]