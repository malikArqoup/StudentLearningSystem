from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from ..serializers import (
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from ..permissions import IsAdminUser
from ..repositories import user_repository


class UserPagination(PageNumberPagination):
    page_size = 10


class UserListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = user_repository.list_all()

        paginator = UserPagination()
        page = paginator.paginate_queryset(users, request)

        serializer = UserListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        password = validated_data.pop("password")
        user = user_repository.create_user(password=password, **validated_data)

        return Response(
            UserListSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        user = user_repository.get_by_id(user_id)

        if user is None:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(UserListSerializer(user).data)

    def patch(self, request, user_id):
        user = user_repository.get_by_id(user_id)

        if user is None:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        user_repository.update_user(user, **serializer.validated_data)

        return Response(UserListSerializer(user).data)

    def delete(self, request, user_id):
        user = user_repository.get_by_id(user_id)

        if user is None:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_repository.deactivate(user)

        return Response(status=status.HTTP_204_NO_CONTENT)
