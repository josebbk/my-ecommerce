# Generated by Django 3.1.4 on 2021-01-10 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_coupon_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
