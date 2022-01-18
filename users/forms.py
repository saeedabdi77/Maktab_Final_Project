from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth.models import User
from .models import Seller, CustomUser
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):

    class Meta:
        model = CustomUser
        fields = ('email', 'password')


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'gender', 'password1', 'password2', 'image')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Seller.objects.create(user=user)
        return user


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)
#
#
# GENDER_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#     )
#
#
# class SignUpForm(UserCreationForm):
#     gender = forms.ChoiceField(
#         required=True,
#         choices=GENDER_CHOICES,
#     )
#     image = forms.ImageField(required=False)
#
#     class Meta:
#         model = CustomUser
#         fields = ('username', 'image', 'gender', 'password1', 'password2', 'email')
#
#
# class UpdateProfilePhotoForm(forms.ModelForm):
#     class Meta:
#         model = Seller
#         fields = ['image']
#
#
# class SetNewPasswordForm(forms.Form):
#     password = forms.CharField(widget=forms.PasswordInput)
#     password1 = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(widget=forms.PasswordInput)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         password1 = cleaned_data.get("password1")
#         password2 = cleaned_data.get("password2")
#
#         if password1 != password2:
#             raise ValidationError(
#                 "password1 and password2 are not equal")
#
#
# class ForgetPasswordForm(forms.Form):
#     email = forms.EmailField()
