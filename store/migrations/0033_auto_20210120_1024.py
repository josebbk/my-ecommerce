# Generated by Django 3.1.4 on 2021-01-20 06:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0032_auto_20210119_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ordered_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]