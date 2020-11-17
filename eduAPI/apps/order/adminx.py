import xadmin
from order.models import Order
from order.models import OrderDetail

xadmin.site.register(Order)
xadmin.site.register(OrderDetail)