from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
# Create your views here.
from course.models import Course, CourseExpire
from django_redis import get_redis_connection

from eduAPI.utils.const import IMG_SRC


class CartAPIView(ViewSet):
    permission_classes = [IsAuthenticated]

    def add_to_cart(self, request):

        course_id = request.data.get('course_id')
        user_id = request.user.id
        print('1', user_id)
        # 默认选中
        select = True
        # 默认永久
        expire_time = 0
        try:
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({
                'message': '课程不存在啦!'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            redis_conn = get_redis_connection('cart')

            # 将数据保存到redis  使用redis管道
            pipeline = redis_conn.pipeline()
            # 保存的是商品的信息以及对应的有效期
            pipeline.hset("cart_%s" % user_id, course_id, expire_time)
            # 商品的勾选状态
            pipeline.sadd("selected_%s" % user_id, course_id)
            # 执行命令
            pipeline.execute()

            # 获取购物车中商品的总数据量
            course_len = redis_conn.hlen("cart_%s" % user_id)
        except:
            return Response({
                'meesage': '添加失败'
            }, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        return Response({
            'message': '添加成功', "cart_length": course_len
        }, status=status.HTTP_200_OK)

    def show_car(self, request):

        user_id = request.user.id

        # 连接redis库
        redis_conn = get_redis_connection('cart')
        # 拿到redis中的用户数据
        cart_list_bytes = redis_conn.hgetall("cart_%s" % user_id)
        selected_list_bytes = redis_conn.smembers("selected_%s" % user_id)

        result = []
        expire_id = 0
        # 从数据库拿到数据 遍历
        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)

            try:
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:
                continue

            result.append({
                # 拿到所有的有效期和对应价格
                'expire_list': course.expire_list,
                'expire_id': expire_id,
                'price': course.real_price(expire_id),
                'course_img': IMG_SRC + course.course_img.url,
                'name': course.name,
                'id': course.id,
                'selected': True if course_id_byte in selected_list_bytes else False,
            })
        return Response({
            'data': result,
        }, status=status.HTTP_200_OK)

    def change_select(self, request):
        user_id = request.user.id
        course_id = request.data.get('course_id')
        course_selected = request.data.get('course_selected')

        conn = get_redis_connection('cart')
        pipeline = conn.pipeline()
        if course_selected:
            # 选中 就添加
            pipeline.sadd("selected_%s" % user_id, course_id)
            # 没勾选 就删掉
        else:
            pipeline.srem('selected_%s' % user_id, course_id)

        # 执行命令
        pipeline.execute()

        cart_list_bytes = conn.hgetall("cart_%s" % user_id)
        selected_list_bytes = conn.smembers("selected_%s" % user_id)
        if len(cart_list_bytes) == len(selected_list_bytes):
            return Response({
                'checked': True,
            })
        return Response({
            'checked': False
        })

    def change_expire(self, request):
        user_id = request.user.id
        course_id = request.data.get('course_id')
        expire_id = request.data.get('expire_id')

        try:
            # 查询课程是否存在
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            if expire_id > 0:
                expire = CourseExpire.objects.filter(is_show=True, is_delete=False, pk=expire_id)
                if not expire:
                    return Response({
                        'message': '课程过期'
                    }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "课程信息不存在"},
                            status=status.HTTP_400_BAD_REQUEST)

        conn = get_redis_connection('cart')
        conn.hset('cart_%s' % user_id, course_id, expire_id)

        return Response({
            'message': '成功修改有效期',
        }, status=status.HTTP_200_OK)

    def delete_course(self, request):
        course_id = request.data.get('course_id')
        user_id = request.user.id
        print(user_id, course_id)
        conn = get_redis_connection('cart')
        pipeline = conn.pipeline()
        # 删除
        pipeline.hdel('cart_%s' % user_id, course_id)
        pipeline.srem('selected_%s' % user_id, course_id)
        # 执行命令
        pipeline.execute()
        course_len = conn.hlen("cart_%s" % user_id)
        return Response({
            'cart_length': course_len
        })


class CarAllCheckedViewset(ViewSet):
    def checked_all(self, request):
        user_id = request.user.id
        checked = request.data.get('checked')
        conn = get_redis_connection('cart')

        # TODO 1 拿到数据库中的所有course_id
        cart_list_bytes = conn.hgetall("cart_%s" % user_id)

        pipeline = conn.pipeline()
        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            # TODO 2 如果勾了全选,则加入到选中数据库
            if checked:
                # 选中 就添加
                pipeline.sadd("selected_%s" % user_id, course_id)
                # 没勾选 就删掉
            else:
                pipeline.srem('selected_%s' % user_id, course_id)

        # 执行命令
        pipeline.execute()
        return Response({'message': 'success'}, status=status.HTTP_200_OK)

    def delete_all(self, request):
        user_id = request.user.id
        conn = get_redis_connection('cart')

        cart_list_bytes = conn.hgetall("cart_%s" % user_id)

        pipeline = conn.pipeline()
        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            pipeline.hdel('cart_%s' % user_id, course_id)
            pipeline.srem('selected_%s' % user_id, course_id)

        pipeline.execute()

        return Response({
            'message': '删除成功',
        })

    def get_order_data(self, request):
        user_id = request.user.id
        conn = get_redis_connection('cart')
        # 商品总价
        total = 0
        # 返回给前端的数据
        data = []
        # 拿到数据库中的数据
        cart_list_bytes = conn.hgetall("cart_%s" % user_id)
        selected_list_bytes = conn.smembers("selected_%s" % user_id)

        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)

            # 如果被选中了
            if course_id_byte in selected_list_bytes:
                try:
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    continue
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

                data.append({
                    'id': course.id,
                    'old_price': old_price,
                    'real_price': real_price,
                    'name': course.name,
                    'course_img': IMG_SRC + course.course_img.url,
                    'expire_text': expire_text,
                })

                total += float(real_price)
        return Response({
            'message': 'ok',
            'data': data,
            'total_price': total
        }, status=status.HTTP_200_OK)
