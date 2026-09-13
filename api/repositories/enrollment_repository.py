from api.models import Enrollment


class EnrollmentRepository:
    def get_by_id(self, enrollment_id):
        try:
            return Enrollment.objects.get(id=enrollment_id)
        except Enrollment.DoesNotExist:
            return None

    def create_enrollment(self, **fields):
        return Enrollment.objects.create(**fields)

    def update_enrollment(self, enrollment, **fields):
        for field, value in fields.items():
            setattr(enrollment, field, value)
        enrollment.save()
        return enrollment


enrollment_repository = EnrollmentRepository()
