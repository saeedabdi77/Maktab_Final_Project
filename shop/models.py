from django.db import models
from django.db.models.signals import pre_save
import random
from django.utils.text import slugify
from django.db.models import Sum, F
from users.models import Address, Seller, CustomUser


class Category(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class StoreType(models.Model):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class Store(models.Model):
    status_choices = (
        ('processing', 'processing'),
        ('confirmed', 'confirmed'),
        ('deleted', 'deleted')
    )
    owner = models.ForeignKey(Seller, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    type = models.ForeignKey(StoreType, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='store')
    address = models.OneToOneField(Address, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=status_choices)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductField(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=50)
    details = models.ManyToManyField(ProductField)

    def __str__(self):
        return self.name


class Product(models.Model):
    status_choices = (
        ('processing', 'processing'),
        ('confirmed', 'confirmed'),
    )
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, unique=False)
    type = models.ForeignKey(ProductType, on_delete=models.PROTECT, blank=True, null=True)
    description = models.TextField()
    price = models.FloatField()
    quantity = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, blank=True)
    status = models.CharField(max_length=10, choices=status_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=100, null=True, blank=True)

    def get_all_images(self):
        return ProductImage.objects.filter(product=self)

    def get_default_image(self):
        return ProductImage.objects.filter(product=self).get(default=True).image

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
        slug = slugify(instance.name)
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
pre_save.connect(pre_save_receiver, sender=Store)


class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    publisher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Product')
    default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.default:
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(default=False)
        elif not ProductImage.objects.filter(product=self.product).filter(default=True).exists():
            self.default = True
        super(ProductImage, self).save(*args, **kwargs)


class ProductRate(models.Model):
    rate_choices = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.IntegerField(choices=rate_choices)

    class Meta:
        unique_together = ['user', 'product']


class ProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.ForeignKey(ProductField, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)

    class Meta:
        unique_together = ['key', 'product']


class Favourite(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)


class Cart(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return self.cartitem_set.aggregate(total_price=Sum(F('quantity') * F('product__price')))['total_price']


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if CartItem.objects.filter(id=self.pk).exists():
            amount = self.quantity - CartItem.objects.get(id=self.pk).quantity
        else:
            amount = self.quantity
        if (self.cart.cartitem_set.exists()) and (
                CartItem.objects.filter(cart__pk=self.cart.pk)[0].product.store != self.product.store):
            raise TypeError
        if amount > Product.objects.get(id=self.product.id).quantity:
            raise ValueError
        Product.objects.filter(id=self.product.id).update(quantity=F('quantity') - amount)
        super(CartItem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        Product.objects.filter(id=self.product.id).update(quantity=F('quantity') + self.quantity)
        super(CartItem, self).delete(*args, **kwargs)

    delete.alters_data = True

    class Meta:
        unique_together = ['cart', 'product']


class Order(models.Model):
    status_choices = (
        ('paid', 'paid'),
        ('processing', 'processing'),
        ('canceled', 'canceled'),
        ('confirmed', 'confirmed')
    )
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=status_choices)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, blank=True, null=True)
