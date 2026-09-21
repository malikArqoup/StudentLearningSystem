from api.models import ExternalCourse, ExternalEnrollment


class ExternalCourseRepository:
    def get_by_id(self, course_id):
        try:
            return ExternalCourse.objects.get(id=course_id)
        except ExternalCourse.DoesNotExist:
            return None

    def get_by_external_id(self, provider, external_id):
        return ExternalCourse.objects.filter(
            provider=provider,
            external_id=external_id,
        ).first()

    def create_or_update_course(self, **data):
        course, _ = ExternalCourse.objects.update_or_create(
            provider=data["provider"],
            external_id=data["external_id"],
            defaults={
                "title": data["title"],
                "description": data.get("description", ""),
                "course_url": data["course_url"],
                "image_url": data.get("image_url", ""),
            },
        )
        return course

    def get_enrollment(self, student, external_course):
        return ExternalEnrollment.objects.filter(
            student=student,
            external_course=external_course,
        ).first()

    def create_enrollment(self, student, external_course, status):
        return ExternalEnrollment.objects.create(
            student=student,
            external_course=external_course,
            status=status,
        )


external_course_repository = ExternalCourseRepository()