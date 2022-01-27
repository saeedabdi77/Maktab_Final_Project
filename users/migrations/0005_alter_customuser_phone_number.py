# Generated by Django 3.2.6 on 2022-01-26 19:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20220123_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '9*********'", regex='(9)[0-9]{9}$')]),
        ),
    ]