from django.urls import path

from index import views

urlpatterns = [
    path('banner/',views.BannerAPIView.as_view()),
    path('nav/',views.NavAPIView.as_view()),
    path('cart_length/',views.GetCartLength.as_view()),

]