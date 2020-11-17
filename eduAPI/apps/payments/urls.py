from django.urls import path
from payments.views import AliPayAPIView, AliResultAPIView

urlpatterns = [
    path('ali_pay/', AliPayAPIView.as_view()),
    path('result/', AliResultAPIView.as_view())
]
