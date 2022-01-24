from django.contrib.auth.backends import ModelBackend
from users.models import CustomUser
import redis


class PasswordBackend(ModelBackend):
    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        try:
            if email:
                i = email
            elif username:
                i = username
            else:
                i = None
            if CustomUser.objects.filter(email__iexact=i).exists():
                user = CustomUser.objects.get(email__iexact=i)
            elif CustomUser.objects.filter(phone_number__iexact=i).exists():
                user = CustomUser.objects.get(phone_number__iexact=i)
            else:
                raise Exception
        except Exception:
            return None

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class OtpBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        phone = email
        try:
            user = CustomUser.objects.get(phone_number__iexact=phone)
        except Exception:
            return None
        else:
            r = redis.Redis(encoding="utf-8", decode_responses=True)
            otp = r.get(f'otp:{phone}')
            if otp and password == otp and self.user_can_authenticate(user):
                r.delete(f'otp:{phone}')
                return user
