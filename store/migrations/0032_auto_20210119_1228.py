# Generated by Django 3.1.4 on 2021-01-19 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_auto_20210119_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ref_code',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]