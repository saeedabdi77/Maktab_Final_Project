from django.views.generic import ListView, TemplateView
from django.contrib.auth import authenticate, login, logout
# from .forms import LoginForm, SignUpForm, UpdateProfilePhotoForm, SetNewPasswordForm, ForgetPasswordForm
from .forms import LoginForm, CustomUserCreationForm, VerifyPhoneNumberForm
from .models import CustomUser, Seller
import random
import string
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
import redis
from datetime import timedelta


class SignUp(CreateView):
    template_name = 'shop-signup.html'
    success_url = reverse_lazy('shop-home')
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        email, password = form.cleaned_data.get('email'), form.cleaned_data.get('password1')
        new_user = authenticate(username=email, password=password)

        subject = f"{form.cleaned_data.get('first_name')} thank you for registering to our website"
        message = 'Hope you enjoy!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)

        login(self.request, new_user)
        return valid


class Login(View):
    form = LoginForm
    template_name = 'shop-login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        if form.is_valid():
            user = authenticate(request, username=username, password=password)
            if not Seller.objects.filter(user=user).exists():
                messages.error(request, 'Email/Phone number or password is incorrect!')
                return redirect(reverse('login'))
            if user is not None:
                login(request, user)
                next = request.GET.get('next')
                if next:
                    return redirect(request.GET.get('next'))
                else:
                    return redirect(reverse('shop-home'))
        messages.error(request, 'Email/Phone number or password is incorrect!')
        return redirect(reverse('login'))


class Logout(View):

    def get(self, request):
        logout(request)
        return redirect(reverse('shop-home'))


class VerifyPhoneNumber(View, LoginRequiredMixin):
    template_name = 'verify-phone-number.html'
    form = VerifyPhoneNumberForm
    login_url = '/accounts/login/'

    def get(self, request, *args, **kwargs):
        phone = request.user.phone_number
        otp = random.randint(1000, 9999)
        print(otp)
        r = redis.Redis()
        r.set(f'verify:{phone}', otp, ex=timedelta(minutes=5))
        return render(request, self.template_name, {'form': self.form})

    def post(self, request, *args, **kwargs):
        phone = request.user.phone_number
        form = self.form(request.POST)
        if form.is_valid():
            r = redis.Redis(encoding="utf-8", decode_responses=True)
            otp = r.get(f'verify:{phone}')
            code = form.cleaned_data.get('code')
            if str(code) == otp:
                request.user.phone_number_verified = True
                request.user.save()
                r.delete(f'verify:{phone}')
                messages.success(request, 'Account verified!')
                return redirect(reverse('shop-home'))
        messages.error(request, 'Wrong code!')
        return render(request, self.template_name, {'form': self.form})


# class ChangeProfilePhoto(LoginRequiredMixin, View):
#     login_url = '/blog/login/'
#     template_name = 'change-profile.html'
#     form = UpdateProfilePhotoForm
#
#     def get(self, request, *args, **kwargs):
#         return render(request, self.template_name, {'form': self.form})
#
#     def post(self, request, *args, **kwargs):
#         form = self.form(request.POST, request.FILES)
#         if form.is_valid():
#             user = request.user.extenduser
#             user.image = form.cleaned_data.get('image')
#             user.save()
#             return redirect(reverse('my-posts'))
#         return render(request, self.template_name, {'form': self.form})
#
#
# @login_required(login_url='/blog/login')
# def set_new_password(request):
#     form = SetNewPasswordForm()
#     if request.method == "POST":
#         form = SetNewPasswordForm(request.POST)
#         if form.is_valid():
#             user = request.user
#             if user.check_password(form.cleaned_data.get('password')):
#                 user.set_password(form.cleaned_data.get('password1'))
#                 user.save()
#                 username = form.cleaned_data.get('username')
#                 password = form.cleaned_data.get('password1')
#                 user = authenticate(username=username, password=password)
#                 login(request, user)
#                 return redirect(reverse('my-posts'))
#
#     return render(request, 'new-password.html', {'form': form})
#
#
# class ForgetPassword(View):
#     form = ForgetPasswordForm
#     template_name = 'forget-password.html'
#
#     def get(self, request, *args, **kwargs):
#         return render(request, self.template_name, {'form': self.form})
#
#     @staticmethod
#     def password_generator():
#         return f'{random.choice(string.ascii_letters)}{random.randint(10000000, 99999999)}'
#
#     def post(self, request, *args, **kwargs):
#         form = self.form(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             if not User.objects.filter(email=email).exists():
#                 messages.error(request, 'email not found!')
#                 return render(request, self.template_name, {'form': self.form})
#             password = self.password_generator()
#             subject = "new password for my blog"
#             message = password
#             email_from = settings.EMAIL_HOST_USER
#             recipient_list = [email]
#             send_mail(subject, message, email_from, recipient_list)
#             user = User.objects.get(email=email)
#             user.set_password(password)
#             user.save()
#             messages.success(request, 'New password is sent to your email')
#             return redirect(reverse('login'))
#         return render(request, self.template_name, {'form': self.form})
#
#
# class ShowUserProfile(View):
#     template_name = 'user-profile.html'
#
#     def get(self, request, username):
#         user_profile = User.objects.get(username=username)
#         posts = user_profile.extenduser.post_set.all().order_by('-created_at')
#         return render(request, self.template_name, {'user_profile': user_profile, 'posts': posts})



