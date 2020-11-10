from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    """课程列表分页器"""
    # 指定获取第几页
    page_query_param = "page"
    # 每页大小
    page_size_query_param = "size"
    # 每页多少个
    page_size = 2
    # 每页最大几个
    max_page_size = 10
