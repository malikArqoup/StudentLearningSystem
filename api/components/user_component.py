from ..repositories import user_repository


class LoginResult:
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_INACTIVE = "account_inactive"

    def __init__(self, status, user=None):
        self.status = status
        self.user = user


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


user_component = UserComponent()
