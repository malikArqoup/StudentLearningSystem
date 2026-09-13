from api.models import Enrollment
from api.repositories import enrollment_repository


class EnrollmentComponent:
    def create_enrollment(self, assigned_by, **fields):
        return enrollment_repository.create_enrollment(
            assigned_by=assigned_by,
            source=Enrollment.Source.ADMIN,
            status=Enrollment.Status.ASSIGNED,
            progress_percent=0,
            **fields,
        )


enrollment_component = EnrollmentComponent()
