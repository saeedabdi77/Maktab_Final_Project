from django.db import models
from django.db.models.signals import pre_save
import random
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    brand = models.OneToOneField(Brand, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=250, unique=False)
    description = models.TextField()
    price = models.FloatField()
    quantity = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50, null=True, blank=True)
    comments = models.ManyToManyField(Comment)

    def availability(self):
        if self.quantity == 0:
            return False
        else:
            return True

    def __str__(self):
        return self.name


def random_number_generator():
    return str(random.randint(100000, 999999))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)
    klass = instance.__class__
    qs_exists = klass.objects.filter(slug=slug).exists()

    if qs_exists:
        new_slug = "{slug}-{random}".format(
            slug=slug, random=random_number_generator())

        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(pre_save_receiver, sender=Product)


class ProductImage(models.Model):
    image = models.ImageField(upload_to='Product')
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    main = models.BooleanField(default=False)


class Favourite(models.Model):
    products = models.ManyToManyField(Product)


class CartItem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)


class Cart(models.Model):
    cart_item = models.ManyToManyField(CartItem)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Order(Cart):
    status_choices = (
        ('paid', 'paid'),
        ('processing', 'processing'),
        ('canceled', 'canceled'),
        ('confirmed', 'confirmed')
    )
    status = models.CharField(max_length=10, choices=status_choices)


class StoreType(models.Model):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class Store(models.Model):
    status_choices = (
        ('processing', 'processing'),
        ('confirmed', 'confirmed')
    )
    name = models.CharField(max_length=50)
    products = models.ManyToManyField(Product)
    type = models.OneToOneField(StoreType, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=status_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # address

    def __str__(self):
        return self.name
