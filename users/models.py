from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from .managers import CustomUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from cities_light.models import City, Region


class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    image = models.ImageField(upload_to='profile', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    province = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    zip_code = models.CharField(max_length=15)
    address_description = models.TextField()

    def __str__(self):
        return self.province.name


class Seller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


    # def get_stores(self):
    #     return self.store__set
    #
    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=CustomUser)
def update_seller_user_signal(sender, instance, created, **kwargs):
    if created:
        Seller.objects.create(user=instance)
    instance.seller.save()


# class ExtendUser(models.Model):
#     user = models.OneToOneField(Seller, on_delete=models.CASCADE)
#
#
#     def __str__(self):
#         return self.user.user.email
#
#
# @receiver(post_save, sender=User)
# def update_extend_user_signal(sender, instance, created, **kwargs):
#     if created:
#         ExtendUser.objects.create(user=instance)
#     instance.extenduser.save()
