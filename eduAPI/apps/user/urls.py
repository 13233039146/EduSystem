from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from user import views

urlpatterns = [
    path('login/',obtain_jwt_token),
    path('get_captcha/',views.Catpcha.as_view()),
    path('regist/',views.UserRegistAPIView.as_view()),
    path('check/',views.RegistCheckAPIView.as_view()),
    path('send_code/',views.SendCodeAPIView.as_view()),
    path('login_check_phone/',views.LoginCheckPhoneAPIView.as_view()),
    path('commit_msg/',views.MsgLoginAPIView.as_view()),

]