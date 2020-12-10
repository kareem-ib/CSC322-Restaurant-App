# Generated by Django 3.1.3 on 2020-12-09 19:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0012_order_is_ordered'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderedOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('dine_in_time', models.DateTimeField(null=True)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('dining_option', models.CharField(choices=[('DI', 'Dine In'), ('D', 'Delivery'), ('P', 'Pickup')], default='D', max_length=2)),
                ('delivery_address', models.CharField(max_length=200, null=True)),
                ('chef_prepared', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.chef')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.customer')),
                ('dishes', models.ManyToManyField(to='restaurant.MenuItems')),
            ],
            options={
                'ordering': ['-order_date'],
            },
        ),
        migrations.CreateModel(
            name='UnorderedOrder',
            fields=[
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='restaurant.customer')),
                ('dishes', models.ManyToManyField(to='restaurant.MenuItems')),
            ],
        ),
        migrations.DeleteModel(
            name='Order',
        ),
    ]