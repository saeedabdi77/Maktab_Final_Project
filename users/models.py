from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cities_light.models import City, Region


class Address(models.Model):
    province = models.ForeignKey(Region, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    zip_code = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.province.name


class ExtendUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    addresses = models.ManyToManyField(Address, blank=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    image = models.ImageField(upload_to='profile', blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_extend_user_signal(sender, instance, created, **kwargs):
    if created:
        ExtendUser.objects.create(user=instance)
    instance.extenduser.save()


class Seller(models.Model):
    user = models.OneToOneField(ExtendUser, on_delete=models.CASCADE)

    # def get_stores(self):
    #     return self.store__set
    #
    # def __str__(self):
    #     return str(self.get_stores())
