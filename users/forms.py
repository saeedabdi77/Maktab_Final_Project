from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Seller, CustomUser
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField()

    class Meta:
        model = CustomUser
        fields = ('username', 'password')


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'gender', 'password1', 'password2', 'image')

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


class VerifyPhoneNumberForm(forms.Form):
    code = forms.IntegerField()


class UpdateProfilePhotoForm(forms.Form):
    image = forms.ImageField()


class SetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise ValidationError(
                "password1 and password2 are not equal")


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField()
