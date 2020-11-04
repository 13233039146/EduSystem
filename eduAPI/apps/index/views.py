from django.shortcuts import render
from rest_framework.generics import ListAPIView
# Create your views here.
from index.models import Banner, Nav
from index.serializer import BannerSerializer, NavSerializer
from index.const import BANNER_MAX


class BannerAPIView(ListAPIView):
    queryset = Banner.objects.filter(is_delete=False, is_show=True).order_by('ordering')[:BANNER_MAX]
    serializer_class = BannerSerializer


class NavAPIView(ListAPIView):
    queryset = Nav.objects.filter(is_delete=False, is_show=True).order_by('ordering')
    serializer_class = NavSerializer
