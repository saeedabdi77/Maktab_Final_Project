# Generated by Django 3.2.6 on 2022-01-02 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20220102_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ximage',
            name='x',
        ),
        migrations.RemoveField(
            model_name='product',
            name='images',
        ),
        migrations.AddField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='shop.product'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='X',
        ),
        migrations.DeleteModel(
            name='XImage',
        ),
    ]
