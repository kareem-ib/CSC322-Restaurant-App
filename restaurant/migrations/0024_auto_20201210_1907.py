# Generated by Django 3.1.3 on 2020-12-11 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0023_auto_20201210_1749'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chef',
            name='compliments',
        ),
        migrations.RemoveField(
            model_name='deliveryperson',
            name='compliments',
        ),
        migrations.AddField(
            model_name='chef',
            name='demotions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='deliveryperson',
            name='demotions',
            field=models.IntegerField(default=0),
        ),
    ]