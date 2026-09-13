from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Course, Enrollment, User


def auth_headers(user):
    access = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {access}"}


class EnrollmentCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/enrollments/"

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="AdminPass123!",
            role="admin",
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com",
            password="InstructorPass123!",
            role="instructor",
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="StudentPass123!",
            role="student",
        )

        self.course = Course.objects.create(
            code="CS101",
            title="Intro to CS",
            slug="intro-to-cs",
            description="desc",
            instructor=self.instructor,
            level="Beginner",
            status=Course.Status.DRAFT,
            is_self_enroll_open=False,
        )

    def _payload(self, student=None, course=None):
        return {
            "student": (student or self.student).id,
            "course": (course or self.course).id,
        }

    def test_admin_can_create_enrollment(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.student, course=self.course
            ).exists()
        )

    def test_assigned_by_is_the_logged_in_admin(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.data["assigned_by"], self.admin.id)

    def test_source_is_automatically_admin(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.data["source"], Enrollment.Source.ADMIN)

    def test_default_status_is_assigned(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.data["status"], Enrollment.Status.ASSIGNED)

    def test_duplicate_enrollment_is_rejected(self):
        self.client.credentials(**auth_headers(self.admin))
        self.client.post(self.url, self._payload(), format="json")

        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            Enrollment.objects.filter(
                student=self.student, course=self.course
            ).count(),
            1,
        )

    def test_non_admin_cannot_create(self):
        self.client.credentials(**auth_headers(self.instructor))
        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create(self):
        response = self.client.post(self.url, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_student_is_rejected(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.post(
            self.url,
            {"student": 999999, "course": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_course_is_rejected(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.post(
            self.url,
            {"student": self.student.id, "course": 999999},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_student_user_cannot_be_enrolled(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.post(
            self.url,
            self._payload(student=self.instructor),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EnrollmentUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email="admin2@example.com",
            password="AdminPass123!",
            role="admin",
        )
        self.instructor = User.objects.create_user(
            email="instructor2@example.com",
            password="InstructorPass123!",
            role="instructor",
        )
        self.student = User.objects.create_user(
            email="student2@example.com",
            password="StudentPass123!",
            role="student",
        )
        self.other_student = User.objects.create_user(
            email="other_student2@example.com",
            password="OtherPass123!",
            role="student",
        )

        self.course = Course.objects.create(
            code="CS201",
            title="Data Structures",
            slug="data-structures",
            description="desc",
            instructor=self.instructor,
            level="Intermediate",
            status=Course.Status.DRAFT,
            is_self_enroll_open=False,
        )
        self.other_course = Course.objects.create(
            code="CS202",
            title="Algorithms",
            slug="algorithms",
            description="desc",
            instructor=self.instructor,
            level="Intermediate",
            status=Course.Status.DRAFT,
            is_self_enroll_open=False,
        )

        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            assigned_by=self.admin,
            source=Enrollment.Source.ADMIN,
            status=Enrollment.Status.ASSIGNED,
        )

        self.url = f"/api/v1/enrollments/{self.enrollment.id}/"

    def test_admin_can_patch_status(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.patch(
            self.url,
            {"status": Enrollment.Status.IN_PROGRESS},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, Enrollment.Status.IN_PROGRESS)

    def test_admin_can_patch_due_date(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.patch(
            self.url,
            {"due_date": "2026-12-31T00:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment.refresh_from_db()
        self.assertIsNotNone(self.enrollment.due_date)

    def test_partial_patch_does_not_require_all_fields(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.patch(
            self.url,
            {"status": Enrollment.Status.DROPPED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_update(self):
        self.client.credentials(**auth_headers(self.instructor))
        response = self.client.patch(
            self.url,
            {"status": Enrollment.Status.COMPLETED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_update(self):
        response = self.client.patch(
            self.url,
            {"status": Enrollment.Status.COMPLETED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_enrollment_returns_404(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.patch(
            "/api/v1/enrollments/999999/",
            {"status": Enrollment.Status.COMPLETED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_immutable_fields_cannot_be_changed_through_patch(self):
        self.client.credentials(**auth_headers(self.admin))
        response = self.client.patch(
            self.url,
            {
                "student": self.other_student.id,
                "course": self.other_course.id,
                "source": Enrollment.Source.SELF,
                "assigned_by": self.instructor.id,
                "progress_percent": "77.00",
                "status": Enrollment.Status.IN_PROGRESS,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.student_id, self.student.id)
        self.assertEqual(self.enrollment.course_id, self.course.id)
        self.assertEqual(self.enrollment.source, Enrollment.Source.ADMIN)
        self.assertEqual(self.enrollment.assigned_by_id, self.admin.id)
        self.assertEqual(self.enrollment.progress_percent, 0)
        self.assertEqual(self.enrollment.status, Enrollment.Status.IN_PROGRESS)
