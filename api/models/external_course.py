from django.conf import settings
from django.db import models


class ExternalCourse(models.Model):
    class Provider(models.TextChoices):
        OPEN_EDX = "OPEN_EDX", "Open edX"

    provider = models.CharField(
        max_length=50,
        choices=Provider.choices,
    )
    external_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course_url = models.URLField()
    image_url = models.URLField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_id"],
                name="unique_external_course_provider_id",
            )
        ]

    def __str__(self):
        return f"{self.provider} - {self.title}"


class ExternalEnrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", "Enrolled"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="external_enrollments",
    )
    external_course = models.ForeignKey(
        ExternalCourse,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ENROLLED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "external_course"],
                name="unique_student_external_course",
            )
        ]

    def __str__(self):
        return f"{self.student_id} - {self.external_course_id}"