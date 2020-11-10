import random
import re
import string

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as rf_status
from rest_framework_jwt.settings import api_settings

from eduAPI.utils import const
from eduAPI.utils.geetest import GeetestLib
from eduAPI.utils.phone_message import Message
from user.login_handler import get_user_by_account
from rest_framework.generics import CreateAPIView

from user.models import UserMsg
from user.serializer import UserModelSerializer

pc_geetest_id = "1ea3ed8b35299a931b6a3883ec4a05be"
pc_geetest_key = "9a13879615c1ae2500e356417cd5bcf9"


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
# 滑块验证码接口
class Catpcha(APIView):
    """
    滑块验证码
    """

    user_id = 0
    status = False

    # pc端获取验证码的方法
    def get(self, request, *args, **kwargs):

        username = request.query_params.get('username')

        user = get_user_by_account(username)
        if user is None:
            return Response({'message': '用户不存在'}, status=rf_status.HTTP_400_BAD_REQUEST, )
        self.user_id = user.id
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    # pc端基于前后端分离校验验证码
    def post(self, request, *args, **kwargs):

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')

        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


# 用户注册接口
class UserRegistAPIView(CreateAPIView):
    queryset = UserMsg.objects.all()
    serializer_class = UserModelSerializer


# 注册检验手机号接口
class RegistCheckAPIView(APIView):
    def get(self, request, *args, **kwargs):
        phone = request.query_params.get('phone')
        if not re.match('^1[3-9]\d{9}$', phone):
            print('手机号格式错误')
            return Response({
                'message': '手机号格式错误'
            }, status=rf_status.HTTP_400_BAD_REQUEST)
        user = get_user_by_account(phone)
        if user is not None:
            print('该手机号已存在')
            return Response({
                'message': '该手机号已存在'
            }, status=rf_status.HTTP_400_BAD_REQUEST)

        return Response({"message": "OK"})


# 发送手机验证码接口
class SendCodeAPIView(APIView):

    def get(self, request, *args, **kwargs):
        phone = request.query_params.get('phone')

        # TODO 1 获取redis连接
        redis_conn = get_redis_connection("sms_code")

        # TODO 2 判断用户60s内是否发送过验证码
        # 首次注册一定没有发送过
        # 使用ssm_来标识这是自动过期的那条code
        ssm_code = redis_conn.get('sms_%s' % phone)
        if ssm_code is not None:
            return Response({
                'message': '您在60s内发送过短信了,请稍等!'
            }, status=rf_status.HTTP_400_BAD_REQUEST)

        # TODO 3 若没有发送过验证码
        # TODO   生成随机验证码
        code = "".join(random.sample([x for x in string.digits], 6))

        # TODO 4 生成验证码要先保存在redis中
        # 保存: (1) 手机号-验证码-自动过期时间(60s)  - 值为code
        #       (2) 手机号-验证码-有效时间    - 值为code
        redis_conn.setex("sms_%s" % phone, const.GET_SSM_SPACE_TIME, code)
        redis_conn.setex("alive_%s" % phone, const.SSM_ALIVE_TIME, code)

        # TODO 5 给用户发送验证码
        try:
            message = Message(const.API_KEY)
            message.send(phone, code)
        except:
            return Response({
                'message': '验证码获取失败'
            }, status=rf_status.HTTP_400_BAD_REQUEST)
        return Response({
            'message': '验证码获取成功'
        }, status=rf_status.HTTP_200_OK)

# 检验登录的手机号
class LoginCheckPhoneAPIView(APIView):
    def get(self, request, *args, **kwargs):
        phone = request.query_params.get('phone')
        flag = UserMsg.objects.filter(phone=phone)

        # 查无此人
        if not flag:
            return Response({
                'message':'您输入的手机号还未被注册!'
            },status=rf_status.HTTP_400_BAD_REQUEST)

        return Response({
            'ok'
        },status=rf_status.HTTP_200_OK)


# 短信登录接口
class MsgLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # 拿到前端传递的数据
        phone = request.data.get('phone')
        code = request.data.get('code')
        print(phone)

        # TODO 1 比较数据库中的手机是否存在
        user = UserMsg.objects.filter(phone=phone).first()

        if not user:
            return Response({
                'message': '您的手机号不存在'
            },status=rf_status.HTTP_400_BAD_REQUEST)

        # TODO 2 检验短信验证码
        redis_conn = get_redis_connection('sms_code')
        redis_code = redis_conn.get('alive_%s' % phone)
        print('两个code: ',redis_code, code)
        if redis_code.decode() != code:
            return Response({
                'message': '您输入的验证码有误!'
            })

        # TODO 手机和验证码都正确
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response({'message':'登录成功',
                         'token': token}, status=rf_status.HTTP_200_OK)
