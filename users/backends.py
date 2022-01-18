from django.contrib.auth.backends import ModelBackend
from users.models import CustomUser


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        try:
            if email:
                i = email
            elif username:
                i = username
            else:
                i = None
            user = CustomUser.objects.get(email__iexact=i)
        except Exception:
            return None

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
