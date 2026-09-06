from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.components import course_component
from api.permissions import IsAuthenticatedUser
from api.serializers import (
    CourseCreateSerializer,
    CourseResponseSerializer,
)


class CourseListCreateView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = course_component.create_course(
            instructor=request.user,
            **serializer.validated_data,
        )

        return Response(
            CourseResponseSerializer(course).data,
            status=status.HTTP_201_CREATED,
        )