from django.urls import path
from .views_api import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='user_register'),
    path('profile/', Profile.as_view(), name='profile'),
    path('otp/', OtpView.as_view(), name='otp'),
    path('verify/send_code/', SendAccountVerificationCodeView.as_view(), name='send_verification_code'),
    path('verify/enter_code/', EnterAccountVerificationCodeView.as_view(), name='enter_verification_code'),
]
