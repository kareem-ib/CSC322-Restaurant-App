# Generated by Django 3.1.3 on 2020-12-09 01:20

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('restaurant', '0007_auto_20201208_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='user_ptr',
        ),
        migrations.DeleteModel(
            name='Chef',
        ),
        migrations.DeleteModel(
            name='DeliveryPerson',
        ),
        migrations.AlterModelOptions(
            name='dish',
            options={'verbose_name': 'Dish', 'verbose_name_plural': 'Dishes'},
        ),
        migrations.CreateModel(
            name='Chef',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
                ('type', models.CharField(choices=[('CHEF', 'Chef'), ('DP', 'Delivery Person')], max_length=50, verbose_name='Type')),
                ('complaints', models.IntegerField(default=0)),
                ('compliments', models.IntegerField(default=0)),
                ('salary', models.DecimalField(decimal_places=2, default=12500, max_digits=7)),
            ],
            options={
                'permissions': [('has_desig_chef', 'Has Designated chef permission')],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryPerson',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
                ('type', models.CharField(choices=[('CHEF', 'Chef'), ('DP', 'Delivery Person')], max_length=50, verbose_name='Type')),
                ('complaints', models.IntegerField(default=0)),
                ('compliments', models.IntegerField(default=0)),
                ('salary', models.DecimalField(decimal_places=2, default=12500, max_digits=7)),
            ],
            options={
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='Dish',
            name='dish_chef',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.chef'),
        ),
        migrations.AlterField(
            model_name='Order',
            name='chef_prepared',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.chef'),
        ),
    ]