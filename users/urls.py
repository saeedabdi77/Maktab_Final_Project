from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', login_account, name='login'),
    path('logout/', logout_account, name='logout'),
    path('signup/', signup, name='signup'),
    path('change-profile/', ChangeProfilePhoto.as_view(), name="change-profile"),
    path('change-password/', set_new_password, name="change-password"),
    path('forgot-password/', ForgetPassword.as_view(), name="forgot-password"),
    path('profile/<str:username>/', ShowUserProfile.as_view(), name="show-profile"),
]
