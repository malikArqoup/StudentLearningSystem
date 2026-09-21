import requests

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.components import external_course_component, ExternalEnrollmentResult
from api.permissions import IsAuthenticatedUser, IsStudentUser
from api.serializers import (
    ExternalCourseResponseSerializer,
    ExternalEnrollmentResponseSerializer,
)


class ExternalCourseListView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        try:
            courses = external_course_component.get_external_courses()
        except requests.RequestException:
            return Response(
                {
                    "detail": "Unable to retrieve courses from external provider."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        serializer = ExternalCourseResponseSerializer(
            courses,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ExternalCourseEnrollView(APIView):
    permission_classes = [IsStudentUser]

    def post(self, request, course_id):
        result = external_course_component.enroll_student(
            student=request.user,
            external_course_id=course_id,
        )

        if result.status == ExternalEnrollmentResult.COURSE_NOT_FOUND:
            return Response(
                {"detail": "External course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if result.status == ExternalEnrollmentResult.ALREADY_ENROLLED:
            return Response(
                {"detail": "Already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if result.status == ExternalEnrollmentResult.PROVIDER_ERROR:
            return Response(
                {
                    "detail": "Unable to complete enrollment with external provider."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            ExternalEnrollmentResponseSerializer(result.enrollment).data,
            status=status.HTTP_201_CREATED,
        )