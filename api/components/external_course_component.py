from api.integrations import open_edx_client
from api.repositories import external_course_repository


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


external_course_component = ExternalCourseComponent()
