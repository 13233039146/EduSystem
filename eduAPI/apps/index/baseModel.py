from django.db import models


class BaseModel(models.Model):
    is_show = models.BooleanField(default=False, verbose_name="展示与否")
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')
    create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateField(auto_now=True, verbose_name='修改时间')
    ordering = models.IntegerField(default=1, verbose_name='序号')
