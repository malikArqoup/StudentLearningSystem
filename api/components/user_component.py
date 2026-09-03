from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password

from ..repositories import user_repository


class LoginResult:
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_INACTIVE = "account_inactive"

    def __init__(self, status, user=None):
        self.status = status
        self.user = user


class ChangePasswordResult:
    SUCCESS = "success"
    INVALID_OLD_PASSWORD = "invalid_old_password"
    PASSWORD_TOO_WEAK = "password_too_weak"

    def __init__(self, status):
        self.status = status


class UserComponent:
    def authenticate(self, email, password):
        user = user_repository.get_by_email(email)

        if user is None or not user.check_password(password):
            return LoginResult(LoginResult.INVALID_CREDENTIALS)

        if not user.is_active:
            return LoginResult(LoginResult.ACCOUNT_INACTIVE)

        return LoginResult(LoginResult.SUCCESS, user)

    def get_full_name(self, user):
        return f"{user.first_name} {user.last_name}".strip()

    def change_password(self, user, old_password, new_password):
        if not user.check_password(old_password):
            return ChangePasswordResult(ChangePasswordResult.INVALID_OLD_PASSWORD)

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError:
            return ChangePasswordResult(ChangePasswordResult.PASSWORD_TOO_WEAK)

        user_repository.set_password(user, new_password)

        return ChangePasswordResult(ChangePasswordResult.SUCCESS)


user_component = UserComponent()
