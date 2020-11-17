from datetime import datetime

from alipay import AliPay
from django.db import transaction
from django_redis import get_redis_connection

from eduAPI.settings import develop as settings
# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from course.models import CourseExpire


from order.models import Order
from payments.models import UserCourse


class AliPayAPIView(APIView):
    def get(self, request, *args, **kwargs):
        order_number = request.query_params.get('order_number')

        # TODO 查询订单是否存在

        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({
                'message': '订单不存在'
            }, status=status.HTTP_400_BAD_REQUEST)

        # TODO 初始化支付宝参数
        alipay = AliPay(
            appid=settings.ALIPAY_CONFIG['appid'],  # 沙箱应用的id
            app_notify_url=settings.ALIPAY_CONFIG['app_notify_url'],  # 默认回调url
            # k开发者私钥
            app_private_key_string=settings.ALIPAY_CONFIG['app_private_key_path'],
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIPAY_CONFIG['alipay_public_key_path'],
            sign_type=settings.ALIPAY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIPAY_CONFIG['debug'],  # 默认False
        )

        # TODO 电脑网站支付 alipay.trade.page.pay
        # 这是订单信息.
        order_string = alipay.api_alipay_trade_page_pay(
            # 支付宝所接受的订单号
            out_trade_no=order.order_number,
            # 总价
            total_amount=float(order.real_price),
            subject=order.order_title,
            return_url=settings.ALIPAY_CONFIG['return_url'],
            notify_url=settings.ALIPAY_CONFIG['notify_url'],  # 可选, 不填则使用默认notify url
        )


        # TODO 生成订单信息 需要将订单信息(order_string)和网关(沙箱地址)拼接
        url = settings.ALIPAY_CONFIG['gateway_url'] + order_string


        return Response(url)


class AliResultAPIView(APIView):
    def get(self, request, *args, **kwargs):

        print('处理开始')
        # TODO 初始化支付宝参数
        alipay = AliPay(
            appid=settings.ALIPAY_CONFIG['appid'],  # 沙箱应用的id
            app_notify_url=settings.ALIPAY_CONFIG['app_notify_url'],  # 默认回调url
            # k开发者私钥
            app_private_key_string=settings.ALIPAY_CONFIG['app_private_key_path'],
            # app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIPAY_CONFIG['alipay_public_key_path'],
            # alipay_public_key_string=alipay_public_key_string,
            sign_type=settings.ALIPAY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIPAY_CONFIG['debug'],  # 默认False
        )

        # TODO 通知验证 Django版本(在github上)
        # 验证支付宝的异步通知，data来自于支付宝回调函数
        data = request.query_params.dict()

        # 获取签名信息
        signature = data.pop("sign")

        # 比对签名是否合法
        success = alipay.verify(data, signature)
        print(success)
        # 成功,则 TODO 进行支付成功的业务逻辑
        if success:

            dic = self.order_result(data)
            return Response({
                'data': dic
            },status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "对不起，订单支付失败"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic()
    # 处理支付成功的业务逻辑
    def order_result(self, data):
        print('支付成功,开始处理')
        # TODO 查询订单是否成功

        order_number = data.get('out_trade_no')

        # 查询订单存在与否
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({
                'message': '订单不存在'
            },status=status.HTTP_400_BAD_REQUEST)

        try:
            # TODO 修改订单状态
            # 支付时间为现在
            order.pay_time = datetime.now()
            # 已支付
            order.order_status = 1
            order.save()

            # TODO 为用户生成购买记录
            # `用户信息,课程信息和流水号`
            user = order.user
            # TODO 问题.ORM
            order_course_list = order.order_courses.all()
            print('course_detail_list', order_course_list)
            # 订单页展示的信息
            course_list = []

            for order_detail in order_course_list:
                course = order_detail.course
                course.students += 1
                course.save()

                # 看购买的课程是不是永久
                pay_time = order.pay_time.timestamp()  # 时间戳
                # 不是永久
                if order_detail.expire > 0:
                    expire = CourseExpire.objects.get(pk=order_detail.expire)

                    # 过期时间
                    expire_timestamp = expire.expire_time * 24 * 60 * 60
                    # 当前时间 + 有效时间 = 最终的过期时间
                    end_time = datetime.fromtimestamp(pay_time + expire_timestamp)
                else:
                    # 永久购买
                    end_time = None

                UserCourse.objects.create(
                    user_id=user.id,
                    course_id=course.id,
                    trade_no=data.get("trade_no"),
                    pay_time=order.pay_time,
                    out_time=end_time,
                )

                course_list.append({
                    "id": course.id,
                    "name": course.name
                })
        except:
            return Response({"message": "对不起，订单相关信息更新失败"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        # TODO  删除该用户购物车中的信息
        conn = get_redis_connection('cart')
        pipeline = conn.pipeline()
        cart_list_bytes = conn.hgetall("cart_%s" % user.id)

        selected_list_bytes = conn.smembers("selected_%s" % user.id)
        aList = []  # 所有选中的课程id
        for i in selected_list_bytes:
            aList.append(int(i))

        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            if course_id in aList:
                pipeline.hdel('cart_%s' % user.id, course_id)
                pipeline.srem('selected_%s' % user.id, course_id)

        pipeline.execute()
        cart_list2 = conn.hgetall("cart_%s" % user.id)
        cart_length = len(cart_list2)

        dic = {"message": "支付成功",
                         "success": "success",
                         "pay_time": order.pay_time.strftime('%Y-%m-%d %H:%M:%S'),
                         "real_price": order.real_price,
                         "course_list": course_list,
                        'cart_length':cart_length}
        return dic