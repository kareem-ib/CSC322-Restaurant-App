# Generated by Django 3.1.3 on 2020-12-10 22:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('restaurant', '0022_auto_20201210_1648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaints',
            name='complainee_id',
        ),
        migrations.RemoveField(
            model_name='complaints',
            name='complainee_type',
        ),
        migrations.RemoveField(
            model_name='complaints',
            name='snitch_id',
        ),
        migrations.RemoveField(
            model_name='complaints',
            name='snitch_type',
        ),
        migrations.AddField(
            model_name='complaints',
            name='recipient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='complaints_recipient', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='complaints',
            name='sender',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='complaints_sender', to=settings.AUTH_USER_MODEL),
        ),
    ]
