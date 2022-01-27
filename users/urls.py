from django.urls import path
from .views import *

urlpatterns = [
    path('change-profile/', ChangeProfilePhoto.as_view(), name="change-profile"),
    path('change-password/', set_new_password, name="change-password"),
    path('forgot-password/', ForgetPassword.as_view(), name="forgot-password"),
    path('profile/<str:email>/', ShowUserProfile.as_view(), name="show-profile"),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('verify_number/', VerifyPhoneNumber.as_view(), name='verify_number'),
]
