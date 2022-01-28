from django.contrib.auth.backends import ModelBackend
from users.models import CustomUser
from django.core.cache import cache


class PasswordBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if username:
                username_field = username
            elif kwargs['phone/email']:
                username_field = kwargs['phone/email']
            else:
                username_field = None
            if CustomUser.objects.filter(email__iexact=username_field).exists():
                user = CustomUser.objects.get(email__iexact=username_field)
            elif CustomUser.objects.filter(phone_number__iexact=username_field).exists():
                user = CustomUser.objects.get(phone_number__iexact=username_field)
            else:
                raise Exception
        except Exception:
            return None

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class OtpBackend(ModelBackend):
    def authenticate(self, request, password=None, **kwargs):
        username_field = kwargs['phone/email']
        try:
            if CustomUser.objects.filter(email__iexact=username_field).exists():
                user = CustomUser.objects.get(email__iexact=username_field)
            elif CustomUser.objects.filter(phone_number__iexact=username_field).exists():
                user = CustomUser.objects.get(phone_number__iexact=username_field)
            else:
                raise Exception
        except Exception:
            return None
        else:
            phone = user.phone_number
            otp = cache.get(f'otp:{phone}')
            if otp and password == str(otp) and self.user_can_authenticate(user):
                cache.delete(f'otp:{phone}')
                return user
