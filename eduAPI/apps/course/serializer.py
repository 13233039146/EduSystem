from rest_framework.serializers import ModelSerializer

from course import models


class CourseCategorySerializer(ModelSerializer):
    class Meta:
        model = models.CourseCategory
        fields = ("id", "name")


class TeacherModelSerializer(ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ["id", "name", "title", "signature", "brief"]


class CourseModelSerializer(ModelSerializer):
    # 因为查询的时候需要教师头像等很多信息,单纯的引入外键不可以,所以需要引入序列化器
    teacher = TeacherModelSerializer()

    class Meta:
        model = models.Course
        fields = ("id", "name", "course_img", "students", "lessons", "pub_lessons", "price",
                  "teacher", "lesson_list")
        # lession_list是一个自定义字段,因为在页面的某个课程需要展示一些课时
        # 而在model类中课时的外键就是课程,


class CourseDetailModelSerializer(ModelSerializer):
    teacher = TeacherModelSerializer()
    """提供课程详情所需的信息"""

    class Meta:
        model = models.Course
        fields = ('id', 'name', 'course_img', 'students', 'lessons', 'pub_lessons', 'price',
                  'teacher', 'level_name', 'course_video')


class CourseLessonSerializer(ModelSerializer):
    class Meta:
        model = models.CourseLesson
        fields = ('id', 'name', 'free_trail')


class CourseChapterSerializer(ModelSerializer):
    # 一对多需要True
    coursesections = CourseLessonSerializer(many=True)

    class Meta:
        model = models.CourseChapter
        fields = ('id', 'chapter', 'name', 'coursesections')
