from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView

from course import serializer
from course import models
from course.pagination import MyPagination


class CourseCategoryAPIView(ListAPIView):
    queryset = models.CourseCategory.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = serializer.CourseCategorySerializer


class LessionAPIView(ListAPIView):
    queryset = models.Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = serializer.CourseModelSerializer

    # 过滤器指定,id分类,排序
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # 查询字段(前端也要使用这个字段传递参数)
    filter_fields = ("course_category",)

    # 指定课程可以排序的条件
    # id排序,人气排序,价格排序
    ordering_fields = ("id", "students", "price")
    # 指定分页的类
    pagination_class = MyPagination


class CourseDetailAPIView(RetrieveAPIView):
    # 查询单个课程信息
    queryset = models.Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = serializer.CourseDetailModelSerializer


# 查询章节
class CourseChapterAndLesson(ListAPIView):
    queryset = models.CourseChapter.objects.filter(is_show=True,is_delete=False).order_by('id')
    serializer_class = serializer.CourseChapterSerializer

    filter_backends = [DjangoFilterBackend]

    # 根据course(外键)查看课时
    filter_fields = ['course']

