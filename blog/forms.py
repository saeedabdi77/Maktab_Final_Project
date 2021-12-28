from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ExtendUser
from django.core.exceptions import ValidationError
from django import forms
from .models import Tag, Post, Category, Comment
from django.contrib.auth.models import User
from .models import ExtendUser
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Contact


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, min_length=5)
    password = forms.CharField(widget=forms.PasswordInput)


GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )


class SignUpForm(UserCreationForm):
    gender = forms.ChoiceField(
        required=True,
        choices=GENDER_CHOICES,
    )
    image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'image', 'gender', 'password1', 'password2', 'email')


class UpdateProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = ExtendUser
        fields = ['image']


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


class EditCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title']


class DeleteCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = []


class EditTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class DeleteTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = []


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['publisher', 'slug', 'likes']


class UpdatePublishedPostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['publisher', 'slug', 'likes', 'status']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
