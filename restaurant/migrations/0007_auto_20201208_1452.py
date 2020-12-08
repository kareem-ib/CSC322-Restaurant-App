# Generated by Django 3.1.3 on 2020-12-08 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0006_auto_20201207_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='tag',
            field=models.CharField(choices=[('SP', 'Specials'), ('A', 'Appetizers'), ('S', 'Salads'), ('C', 'Chicken'), ('B', 'Beef'), ('P', 'Pork'), ('D', 'Desserts')], max_length=2),
        ),
    ]
