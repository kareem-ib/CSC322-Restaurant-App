# Generated by Django 3.1.3 on 2020-12-09 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0010_auto_20201208_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='image',
            field=models.ImageField(upload_to='img'),
        ),
    ]