from django.db import transaction
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from rest_framework.generics import CreateAPIView
from order.serialzer import OrderSerializer

from order.models import Order


@method_decorator(transaction.atomic(), name='dispatch')
class OrderCreateAPIView(CreateAPIView):
    queryset = Order.objects.filter(is_delete=False, is_show=True)
    serializer_class = OrderSerializer
