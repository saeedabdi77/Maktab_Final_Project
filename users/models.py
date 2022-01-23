from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager
from cities_light.models import City, Region
from versatileimagefield.fields import VersatileImageField, PPOIField
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(regex=r'(9)[0-9]{9}$',
                                 message="Phone number must be entered in the format: '9*********'")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True, unique=True)
    phone_number_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    image = VersatileImageField(
        'Image',
        upload_to='profile/',
        ppoi_field='image_ppoi',
        blank=True,
        null=True
    )
    image_ppoi = PPOIField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

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

    def __str__(self):
        return str(self.user)

# @receiver(post_save, sender=CustomUser)
# def update_seller_user_signal(sender, instance, created, **kwargs):
#     if created:
#         Seller.objects.create(user=instance)
#     instance.seller.save()


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
