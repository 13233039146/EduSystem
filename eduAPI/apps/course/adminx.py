import xadmin
from course import models


class CourseCategoryAdminx(object):
    pass


xadmin.site.register(models.CourseCategory, CourseCategoryAdminx)


class CourseModelAdmin(object):
    """课程表"""
    pass


xadmin.site.register(models.Course, CourseModelAdmin)


class CourseChapterModelAdmin(object):
    """章节表"""
    pass


xadmin.site.register(models.CourseChapter, CourseChapterModelAdmin)


class CourseLessonModelAdmin(object):
    """课时表"""
    pass


xadmin.site.register(models.CourseLesson, CourseLessonModelAdmin)


class TeacherModelAdmin(object):
    """教师表"""
    pass


xadmin.site.register(models.Teacher, TeacherModelAdmin)
