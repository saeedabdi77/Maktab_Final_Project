from django.db import models
from django.template.defaultfilters import slugify
from django.utils.text import slugify
import random
from django.db.models.signals import pre_save
from users.models import Seller


class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)


class Post(models.Model):
    status_choices = (
        ('draft', 'draft'),
        ('published', 'published')
    )
    title = models.CharField(max_length=50)
    caption = models.TextField()
    publisher = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='post')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=10, choices=status_choices)

    def __str__(self):
        return self.title


class Comment(models.Model):
    parent = models.ForeignKey('Comment', blank=True, null=True, on_delete=models.CASCADE)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Seller, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(Seller, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'user']


class DisLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(Seller, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'user']


def random_number_generator():
    return str(random.randint(100, 999)) + '-' + str(random.randint(10, 99))


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


pre_save.connect(pre_save_receiver, sender=Post)


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.email
