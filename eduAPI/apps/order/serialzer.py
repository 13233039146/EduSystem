from datetime import datetime

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from course.models import Course, CourseExpire
from order.models import Order, OrderDetail


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        # 订单id 订单号 支付类型
        fields = ('id', 'order_number', 'pay_type')
        # 订单id和订单号要序列化给前端
        extra_kwargs = {
            'id': {
                'read_only': True,
            },
            'order_number': {
                'read_only': True,
            },
            'pay_type': {
                'write_only': True,
            }
        }

    # 校验支付方式
    def validate(self, attrs):
        """对数据进行校验"""
        pay_type = attrs.get("pay_type")

        try:
            Order.pay_choices[pay_type]
        except Order.DoesNotExist:
            raise serializers.ValidationError("您当前选择的支付方式不允许~")

        return attrs

    # 生成订单
    def create(self, validated_data):

        # 拿到request对象中的用户token的id
        user_id = self.context['request'].user.id
        print(self.context)
        conn = get_redis_connection('cart')
        # 自增数字
        incr = conn.incr('number')

        # TODO  生成唯一的订单号  时间戳+用户ID+随机字符串
        order_number = datetime.now().strftime("%Y%m%d%H%M%S") + "%06d" % user_id + "%06d" % incr
        # TODO  生成订单
        print(order_number)
        order = Order.objects.create(
            order_title='淘宝!Taobao!',
            total_price=0,
            real_price=0,
            order_number=order_number,
            order_status=0,
            pay_type=validated_data.get('pay_type'),
            credit=0,
            coupon=0,
            order_desc='清仓大甩卖,买完不后悔!',
            user_id=user_id,
        )
        # TODO 生成订单详情
        """
        1. 获取购物车中所有被勾选的商品
        2. 判断商品是否在已勾选的列表中
        3. 判断课程的状态是否正常  不正常直接抛出异常
        4. 判断商品的有效期  根据有效期计算商品优惠后的价格
        5. 生成订单详情。
        6. 计算订单的总价  原价
        """
        cart_list_bytes = conn.hgetall("cart_%s" % user_id)
        # TODO 1 获取购物车中所有被勾选的商品
        selected_list_bytes = conn.smembers("selected_%s" % user_id)

        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)

            # TODO 2 判断商品是否在已勾选的列表中
            if course_id_byte in selected_list_bytes:
                try:
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:

                    # TODO 3 判断课程的状态是否正常  不正常直接抛出异常
                    raise serializers.ValidationError("对不起，您所购买的商品不存在")
                # 默认永久有效
                old_price = course.real_price(0)
                expire_text = '永久有效'

                # 有效期不是永久的
                if expire_id > 0:
                    course_expire = CourseExpire.objects.get(pk=expire_id)
                    old_price = course_expire.price
                    expire_text = course_expire.expire_text

                # 折后价格
                real_price = course.real_price(expire_id)
                try:
                    OrderDetail.objects.create(
                        order=order,
                        course=course,
                        expire=expire_id,
                        price=old_price,  # 原价
                        real_price=real_price,  # 折后价
                        discount_name=course.discount_name,
                    )
                except:
                    raise serializers.ValidationError('该订单项生成失败')

                order.total_price += float(old_price)
                order.real_price += float(real_price)
            order.save()

        return order
