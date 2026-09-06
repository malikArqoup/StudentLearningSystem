from django.utils.text import slugify

from api.models import Course
from api.repositories import course_repository


class CourseComponent:
    def create_course(self, instructor, **fields):
        slug = slugify(fields["title"])

        return course_repository.create_course(
            instructor=instructor,
            slug=slug,
            status=Course.Status.DRAFT,
            **fields,
        )


course_component = CourseComponent()