from api.models import Course


class CourseRepository:
    def create_course(self, **fields):
        return Course.objects.create(**fields)


course_repository = CourseRepository()