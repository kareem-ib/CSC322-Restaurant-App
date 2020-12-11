# Generated by Django 3.1.3 on 2020-12-11 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0038_deliveryperson_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryperson',
            name='avg_rating',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='deliveryperson',
            name='number_ratings',
            field=models.IntegerField(default=0),
        ),
    ]
