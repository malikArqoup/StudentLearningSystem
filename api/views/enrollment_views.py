from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.components import enrollment_component
from api.permissions import IsAdminUser
from api.repositories import enrollment_repository
from api.serializers import (
    EnrollmentCreateSerializer,
    EnrollmentUpdateSerializer,
    EnrollmentResponseSerializer,
)


class EnrollmentListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        enrollment = enrollment_component.create_enrollment(
            assigned_by=request.user,
            **serializer.validated_data,
        )

        return Response(
            EnrollmentResponseSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )


class EnrollmentDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, enrollment_id):
        enrollment = enrollment_repository.get_by_id(enrollment_id)

        if enrollment is None:
            return Response(
                {"detail": "Enrollment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EnrollmentUpdateSerializer(
            enrollment,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        enrollment_repository.update_enrollment(enrollment, **serializer.validated_data)

        return Response(EnrollmentResponseSerializer(enrollment).data)
