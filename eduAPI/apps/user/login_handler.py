from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from user.models import UserMsg


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "username": user.username,
    }


# 多条件登录封装为方法
def get_user_by_account(account):
    try:
        user = UserMsg.objects.filter(Q(username=account) | Q(phone=account) | Q(email=account)).first()
    except UserMsg.DoesNotExist:
        return None
    else:
        return user


# 多条件登录
class UserAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user and user.check_password(password) and user.is_authenticated:
            return user
        else:
            return None
