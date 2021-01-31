# Generated by Django 3.1.4 on 2021-01-11 08:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_auto_20210110_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='ref_code',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='refund',
            name='refund_requested_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
