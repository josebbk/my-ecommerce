# Generated by Django 3.1.4 on 2021-01-16 11:20

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_auto_20210114_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='city',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.customer'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='phone_number',
            field=models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator(message='Insert A Valid Phone Number Like: 0911*****21.', regex='(0|\\+98)?([ ]|-|[()]){0,2}9[0|1|2|3|4]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}')]),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='state_province',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
