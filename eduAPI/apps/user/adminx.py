import xadmin

from user.models import UserMsg

# 注册到后台
class UserInfo(object):
    list_display = ["username", "phone"]


# xadmin.site.register(UserMsg, UserInfo)