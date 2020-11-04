# 配置全局异常处理
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status


def except_handler(exc, content):
    error = "%s %s %s" % (content['view'], content['request'].method, exc)

    print(error)

    response = exception_handler(exc, content)
    if response is None:
        return Response({
            "error_message": "别急,程序员正在火速处理中",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
