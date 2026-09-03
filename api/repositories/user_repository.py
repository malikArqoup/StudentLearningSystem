from ..models import User


class UserRepository:
    def get_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def list_all(self):
        return User.objects.all().order_by("-date_joined")

    def create_user(self, password, **fields):
        user = User(**fields)
        user.set_password(password)
        user.save()
        return user

    def update_user(self, user, **fields):
        for field, value in fields.items():
            setattr(user, field, value)
        user.save()
        return user

    def set_password(self, user, new_password):
        user.set_password(new_password)
        user.save()
        return user

    def deactivate(self, user):
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user


user_repository = UserRepository()
