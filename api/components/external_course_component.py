import requests

from api.integrations import open_edx_client
from api.models import ExternalEnrollment
from api.repositories import external_course_repository


class ExternalEnrollmentResult:
    SUCCESS = "success"
    COURSE_NOT_FOUND = "course_not_found"
    ALREADY_ENROLLED = "already_enrolled"
    PROVIDER_ERROR = "provider_error"

    def __init__(self, status, enrollment=None):
        self.status = status
        self.enrollment = enrollment


class ExternalCourseComponent:
    def get_external_courses(self):
        courses = open_edx_client.get_courses()

        normalized_courses = []

        for course_data in courses:
            external_course_repository.create_or_update_course(
                **course_data
            )

            normalized_courses.append(course_data)

        return normalized_courses

    def enroll_student(self, student, external_course_id):
        external_course = external_course_repository.get_by_id(
            external_course_id
        )

        if external_course is None:
            return ExternalEnrollmentResult(
                ExternalEnrollmentResult.COURSE_NOT_FOUND
            )

        existing_enrollment = external_course_repository.get_enrollment(
            student, external_course
        )

        if existing_enrollment is not None:
            return ExternalEnrollmentResult(
                ExternalEnrollmentResult.ALREADY_ENROLLED
            )

        try:
            open_edx_client.enroll_student(
                course_id=external_course.external_id,
                student_email=student.email,
            )
        except requests.RequestException:
            return ExternalEnrollmentResult(
                ExternalEnrollmentResult.PROVIDER_ERROR
            )

        enrollment = external_course_repository.create_enrollment(
            student=student,
            external_course=external_course,
            status=ExternalEnrollment.Status.ENROLLED,
        )

        return ExternalEnrollmentResult(
            ExternalEnrollmentResult.SUCCESS,
            enrollment,
        )


external_course_component = ExternalCourseComponent()
