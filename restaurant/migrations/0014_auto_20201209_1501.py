# Generated by Django 3.1.3 on 2020-12-09 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0013_auto_20201209_1458'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UnorderedOrder',
            new_name='Cart',
        ),
        migrations.RenameModel(
            old_name='OrderedOrder',
            new_name='Orders',
        ),
    ]
