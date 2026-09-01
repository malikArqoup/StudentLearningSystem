from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
        ]


class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "phone",
            "avatar",
            "timezone",
            "locale",
        ]


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "is_active",
            "date_joined",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
            "student_number",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_role(self, value):
        allowed_roles = ["student", "instructor"]

        if value not in allowed_roles:
            raise serializers.ValidationError(
                "Role must be either student or instructor."
            )

        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "role",
            "is_active",
        ]

    def validate_role(self, value):
        allowed_roles = ["student", "instructor"]

        if value not in allowed_roles:
            raise serializers.ValidationError(
                "Role must be either student or instructor."
            )

        return value