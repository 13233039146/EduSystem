from django.urls import path

from course.views import CourseCategoryAPIView, LessionAPIView

urlpatterns = [
    path('category/',CourseCategoryAPIView.as_view()),
    path('lesson/',LessionAPIView.as_view()),

]