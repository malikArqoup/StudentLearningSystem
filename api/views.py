from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .models import User
from .serializers import (
    RegisterSerializer,
    MeUpdateSerializer,
    UserListSerializer,
    UserCreateSerializer,
)
from .permissions import IsAuthenticatedUser, IsAdminUser


class HealthView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "version": "1.0.0"
        })


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "is_verified": user.is_verified,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is None or not user.check_password(password):
            return Response(
                {
                    "error": {
                        "code": "invalid_credentials"
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {
                    "error": {
                        "code": "account_inactive"
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "role": user.role,
                "institution_id": user.institution_id,
                "avatar": user.avatar,
            }
        })


class RefreshView(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data)


class LogoutView(APIView):
    def post(self, request):
        refresh = request.data.get("refresh")

        if not refresh:
            return Response(
                {
                    "error": {
                        "code": "refresh_required"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "role": user.role,
            "institution_id": user.institution_id,
            "avatar": user.avatar,
            "profile": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "timezone": user.timezone,
                "locale": user.locale,
            }
        })

    def patch(self, request):
        serializer = MeUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.get(request)


class UserPagination(PageNumberPagination):
    page_size = 10


class UserListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by("-date_joined")

        paginator = UserPagination()
        page = paginator.paginate_queryset(users, request)

        serializer = UserListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserListSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )