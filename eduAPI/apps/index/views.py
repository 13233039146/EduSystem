from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import ListAPIView
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from index.models import Banner, Nav
from index.serializer import BannerSerializer, NavSerializer
from eduAPI.utils.const import BANNER_MAX


class BannerAPIView(ListAPIView):
    queryset = Banner.objects.filter(is_delete=False, is_show=True).order_by('ordering')[:BANNER_MAX]
    serializer_class = BannerSerializer


class NavAPIView(ListAPIView):
    queryset = Nav.objects.filter(is_delete=False, is_show=True).order_by('ordering')
    serializer_class = NavSerializer


class GetCartLength(APIView):
    def get(self, request):
        try:
            user_id = request.user.id
            conn = get_redis_connection('cart')
            cart_list_bytes = conn.hgetall("cart_%s" % user_id)
            length = len(cart_list_bytes)
            return Response({
                'cart_length': length
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'cart_length': 0,
            }, status=status.HTTP_400_BAD_REQUEST)
