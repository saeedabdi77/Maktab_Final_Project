from django.contrib.auth import authenticate, login, logout
from .forms import UpdateProfilePhotoForm, SetNewPasswordForm, ForgetPasswordForm, LoginForm, CustomUserCreationForm, \
    VerifyPhoneNumberForm
from .models import CustomUser
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
from django.core.cache import cache


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

    def get(self, request):
        return render(request, self.template_name, {'form': self.form})

    def post(self, request):
        form = self.form(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        if form.is_valid():
            user = authenticate(request, username=username, password=password)
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
        return redirect(reverse('login'))


class VerifyPhoneNumber(View, LoginRequiredMixin):
    template_name = 'verify-phone-number.html'
    form = VerifyPhoneNumberForm
    login_url = '/accounts/login/'

    def get(self, request):
        phone = request.user.phone_number
        otp = random.randint(1000, 9999)
        print('otp:', otp)
        cache.set(f'verify:{phone}', otp, timeout=300)
        time = cache.ttl(f'verify:{phone}')
        return render(request, self.template_name, {'form': self.form, 'time': time})

    def post(self, request):
        phone = request.user.phone_number
        form = self.form(request.POST)
        if form.is_valid():
            otp = cache.get(f'verify:{phone}')
            code = form.cleaned_data.get('code')
            if code == otp:
                request.user.phone_number_verified = True
                request.user.save()
                cache.delete(f'verify:{phone}')
                messages.success(request, 'Account verified!')
                return redirect(reverse('shop-home'))
        messages.error(request, 'Wrong code!')
        time = cache.ttl(f'verify:{phone}')
        return render(request, self.template_name, {'form': self.form, 'time': time})


class ChangeProfilePhoto(LoginRequiredMixin, View):
    login_url = '/blog/login/'
    template_name = 'change-profile.html'
    form = UpdateProfilePhotoForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form})

    def post(self, request):
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            print(form.cleaned_data.get('image'))
            user.image = form.cleaned_data.get('image')
            user.save()
            return redirect(reverse('my-posts'))
        return render(request, self.template_name, {'form': self.form})


@login_required(login_url='/blog/login')
def set_new_password(request):
    form = SetNewPasswordForm()
    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data.get('password')):
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                email = request.user.email
                password = form.cleaned_data.get('password1')
                user = authenticate(email=email, password=password)
                login(request, user)
                return redirect(reverse('my-posts'))

    return render(request, 'new-password.html', {'form': form})


class ForgetPassword(View):
    form = ForgetPasswordForm
    template_name = 'forget-password.html'

    def get(self, request):
        return render(request, self.template_name, {'form': self.form})

    @staticmethod
    def password_generator():
        return f'{random.choice(string.ascii_letters)}{random.randint(10000000, 99999999)}'

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if not CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'email not found!')
                return render(request, self.template_name, {'form': self.form})
            password = self.password_generator()
            subject = "new password for my blog"
            message = password
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            user = CustomUser.objects.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(request, 'New password is sent to your email')
            return redirect(reverse('login'))
        return render(request, self.template_name, {'form': self.form})


class ShowUserProfile(View):
    template_name = 'user-profile.html'

    def get(self, request, email):
        user_profile = CustomUser.objects.get(email=email)
        posts = user_profile.post_set.all().order_by('-created_at')
        return render(request, self.template_name, {'user_profile': user_profile, 'posts': posts})
