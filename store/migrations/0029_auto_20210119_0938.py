# Generated by Django 3.1.4 on 2021-01-19 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_auto_20210116_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='customer',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='store.customer'),
        ),
    ]
