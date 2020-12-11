# Generated by Django 3.1.3 on 2020-12-10 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0020_auto_20201210_1241'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snitch_type', models.CharField(choices=[('C', 'Customer'), ('DP', 'Delivery Person')], max_length=4)),
                ('snitch_id', models.IntegerField()),
                ('complainee_type', models.CharField(choices=[('C', 'Customer'), ('DP', 'Delivery Person'), ('CH', 'Chef')], max_length=4)),
                ('complainee_id', models.IntegerField()),
                ('complaint_body', models.TextField(max_length=2000)),
                ('dispute_body', models.TextField(max_length=2000)),
                ('is_disputed', models.BooleanField(default=False)),
                ('is_processed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Complaint',
                'verbose_name_plural': 'Complaints',
            },
        ),
        migrations.CreateModel(
            name='Compliments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_type', models.CharField(choices=[('C', 'Customer'), ('DP', 'Delivery Person')], max_length=2)),
                ('sender_id', models.IntegerField()),
                ('recipient_type', models.CharField(choices=[('C', 'Customer'), ('DP', 'Delivery Person'), ('CH', 'Chef')], max_length=2)),
                ('recipient_id', models.IntegerField()),
                ('body', models.TextField(max_length=2000)),
                ('is_processed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Compliment',
                'verbose_name_plural': 'Compliments',
            },
        ),
        migrations.DeleteModel(
            name='ComplaintCompliment',
        ),
        migrations.DeleteModel(
            name='UnproccessedComplaint',
        ),
        migrations.AlterField(
            model_name='report',
            name='dispute_body',
            field=models.TextField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_body',
            field=models.TextField(max_length=2000),
        ),
    ]