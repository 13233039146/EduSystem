from django.urls import path

from course.views import CourseCategoryAPIView, LessionAPIView, CourseDetailAPIView, CourseChapterAndLesson

urlpatterns = [
    path('category/',CourseCategoryAPIView.as_view()),
    path('lesson/',LessionAPIView.as_view()),
    path('detail/<str:pk>/',CourseDetailAPIView.as_view()),
    path('chapter/',CourseChapterAndLesson.as_view()),
]