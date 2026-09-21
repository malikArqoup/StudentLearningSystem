import requests

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.components import external_course_component
from api.permissions import IsAuthenticatedUser
from api.serializers import ExternalCourseResponseSerializer


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
