# Generated by Django 4.2 on 2023-06-07 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_alter_practitioner_stage_of_threma'),
    ]

    operations = [
        migrations.AlterField(
            model_name='practitioner',
            name='bob',
            field=models.DateField(),
        ),
    ]
