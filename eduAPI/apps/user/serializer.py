import random
import re
from django.core.cache import cache
from django_redis import get_redis_connection
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from user.login_handler import get_user_by_account
from user.models import UserMsg
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserModelSerializer(ModelSerializer):
    print('hhhhha')
    # 自定义字段,token要参与序列化传给前端
    token = serializers.CharField(max_length=1024, help_text='用户token', read_only=True)
    code = serializers.CharField(help_text='手机短信验证码', write_only=True)

    class Meta:
        model = UserMsg
        # 指定字段,用户名,token参与序列化,手机号密码只是用来注册,参与反序列化
        fields = ('username', 'password', 'phone', 'token', 'code')
        extra_kwargs = {
            'username': {
                'read_only': True
            },
            'password': {
                'write_only': True
            },
            'phone': {
                'write_only': True
            },
        }

    # 全局钩子 做校验
    def validate(self, attrs):
        print(attrs)

        phone = attrs.get('phone')
        code = attrs.get('code')
        password = attrs.get('password')
        print(phone, code, password)

        # TODO 1.检验用户手机号的合法性
        if not re.match(r'^1[3-9]\d{9}$', phone):
            print('手机号格式错误')
            raise serializers.ValidationError('手机号格式错误!')

        # TODO 2 检验手机号是否存在
        try:
            u = get_user_by_account(phone)
        except:
            # 手机号不存在
            u = None
        if u:
            print('该手机号已被注册')
            raise serializers.ValidationError('该手机号已被注册!')
        # TODO 3 检验密码格式

        if len(password) < 8 or len(password) > 16:
            raise serializers.ValidationError('密码格式错误')

        # TODO 4 校验验证码是否正确
        conn = get_redis_connection('sms_code')
        ssm_code = conn.get("alive_%s" % phone)
        print(ssm_code, code, phone)
        if ssm_code.decode() != code:
            raise serializers.ValidationError("验证码不一致")
        # TODO 删除数据库中验证码

        cache.delete_pattern('alive_' + phone)
        cache.delete_pattern('sms_' + phone)
        # TODO 限制用户拿验证码的次数

        return attrs

    # TODO 为什么需要自定义create方法
    #  答案: 1 密码存储需要加密 2 给一个默认用户名 3 给一个token来给到前端
    def create(self, validated_data):
        print(validated_data)

        # 随机字符串
        ran_s = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 5))

        # TODO 1 获取手机号,密码,设置默认用户名
        username = validated_data.get('phone') + ran_s
        phone = validated_data.get('phone')
        password = validated_data.get('password')
        # TODO 2 对密码进行加密
        hash_pwd = make_password(password)
        # TODO 3 保存
        user = UserMsg.objects.create(
            username=username,
            password=hash_pwd,
            phone=phone
        )
        # TODO 4 为用户生成token(签发token)

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user
