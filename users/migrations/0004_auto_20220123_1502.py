# Generated by Django 3.2.6 on 2022-01-23 11:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=10, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '999 999 9999'. Up to 10 digits allowed.", regex='^\\+?1?\\d{9,10}$')]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_number_verified',
            field=models.BooleanField(default=False),
        ),
    ]