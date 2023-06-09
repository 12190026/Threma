# Generated by Django 4.2 on 2023-06-06 19:28

import cloudinary.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_transfer_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='executivemember',
            name='profile_pic',
            field=cloudinary.models.CloudinaryField(default='profile-icon-login-head-icon-vector_teheof.jpg', max_length=255, verbose_name='profile_pics'),
        ),
        migrations.AlterField(
            model_name='practitioner',
            name='cid',
            field=models.BigIntegerField(max_length=11, primary_key=True, serialize=False, validators=[django.core.validators.MinLengthValidator(11)]),
        ),
        migrations.AlterField(
            model_name='practitioner',
            name='contact_no',
            field=models.IntegerField(validators=[django.core.validators.MinLengthValidator(8)]),
        ),
    ]
