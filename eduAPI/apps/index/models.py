from django.db import models
from index.baseModel import BaseModel


# Create your models here.


class Banner(BaseModel):
    img = models.ImageField(upload_to='banner', max_length=255, verbose_name='轮播图')
    title = models.CharField(max_length=100, verbose_name='标题')
    link = models.CharField(max_length=255, verbose_name='链接')

    class Meta:
        db_table = 't_banner'
        verbose_name = '轮播图表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Nav(BaseModel):
    POSITION = (
        (1, 'header'),
        (2, 'footer')
    )
    title = models.CharField(max_length=50,verbose_name='导航标题')
    link = models.CharField(max_length=255,verbose_name='链接')
    position = models.IntegerField(choices=POSITION,default=1,verbose_name='位置')
    is_site =models.BooleanField(default=False, verbose_name='是否为外部链接')

    class Meta:
        db_table = 't_nav'
        verbose_name = '导航栏表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title