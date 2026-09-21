from django.urls import path

from .views import (
    HealthView,
    RegisterView,
    LoginView,
    RefreshView,
    LogoutView,
    MeView,
    ChangePasswordView,
    UserListCreateView,
    UserDetailView,
    CourseListCreateView,
    EnrollmentListCreateView,
    EnrollmentDetailView,
    ExternalCourseListView,
    ExternalCourseEnrollView,
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),

    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path(
        "auth/password/change/",
        ChangePasswordView.as_view(),
        name="password-change",
    ),

    path("users/", UserListCreateView.as_view(), name="users"),
    path(
        "users/<int:user_id>/",
        UserDetailView.as_view(),
        name="user-detail",
    ),

    path(
        "courses/",
        CourseListCreateView.as_view(),
        name="courses",
    ),

    path(
        "enrollments/",
        EnrollmentListCreateView.as_view(),
        name="enrollments",
    ),
    path(
        "enrollments/<int:enrollment_id>/",
        EnrollmentDetailView.as_view(),
        name="enrollment-detail",
    ),
    path(
        "external-courses/",
        ExternalCourseListView.as_view(),
        name="external-courses",
    ),
    path(
        "external-courses/<int:course_id>/enroll/",
        ExternalCourseEnrollView.as_view(),
        name="external-course-enroll",
    ),
]