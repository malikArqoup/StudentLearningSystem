from rest_framework import serializers

from .models import Course, Enrollment, ExternalEnrollment, User


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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


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


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "code",
            "title",
            "description",
            "level",
            "is_self_enroll_open",
        ]


class CourseResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "slug",
            "status",
            "instructor",
        ]


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "student",
            "course",
            "due_date",
        ]

    def validate_student(self, value):
        if value.role != "student":
            raise serializers.ValidationError(
                "Selected user is not a student."
            )

        return value


class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "status",
            "due_date",
        ]


class EnrollmentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "course",
            "assigned_by",
            "source",
            "status",
            "due_date",
            "progress_percent",
            "created_at",
        ]


class ExternalCourseResponseSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    provider = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(
        allow_blank=True,
        required=False,
    )
    course_url = serializers.URLField(
        allow_blank=True,
        required=False,
    )
    image_url = serializers.URLField(
        allow_blank=True,
        required=False,
    )


class ExternalEnrollmentResponseSerializer(serializers.ModelSerializer):
    course_url = serializers.SerializerMethodField()

    class Meta:
        model = ExternalEnrollment
        fields = [
            "id",
            "student",
            "external_course",
            "status",
            "created_at",
            "course_url",
        ]

    def get_course_url(self, obj):
        return obj.external_course.course_url