from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from ..serializers import (
    RegisterSerializer,
    MeUpdateSerializer,
    ChangePasswordSerializer,
)
from ..permissions import IsAuthenticatedUser
from ..components import user_component, LoginResult, ChangePasswordResult
from ..repositories import user_repository


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            password = validated_data.pop("password")
            user = user_repository.create_user(password=password, **validated_data)

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

        result = user_component.authenticate(email, password)

        if result.status == LoginResult.INVALID_CREDENTIALS:
            return Response(
                {
                    "error": {
                        "code": "invalid_credentials"
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if result.status == LoginResult.ACCOUNT_INACTIVE:
            return Response(
                {
                    "error": {
                        "code": "account_inactive"
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )

        user = result.user
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user_component.get_full_name(user),
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
            "full_name": user_component.get_full_name(user),
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
        user_repository.update_user(request.user, **serializer.validated_data)

        return self.get(request)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = user_component.change_password(
            request.user,
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"],
        )

        if result.status == ChangePasswordResult.INVALID_OLD_PASSWORD:
            return Response(
                {
                    "error": {
                        "code": "invalid_old_password"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if result.status == ChangePasswordResult.PASSWORD_TOO_WEAK:
            return Response(
                {
                    "error": {
                        "code": "password_too_weak"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
