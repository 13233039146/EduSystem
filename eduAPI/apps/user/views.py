from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as rf_status
from eduAPI.utils.geetest import GeetestLib
from user.login_handler import get_user_by_account
from user.models import UserMsg

pc_geetest_id = "1ea3ed8b35299a931b6a3883ec4a05be"
pc_geetest_key = "9a13879615c1ae2500e356417cd5bcf9"


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
            return Response({
                'status': rf_status.HTTP_400_BAD_REQUEST,
                'message': '用户不存在'
            })
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

