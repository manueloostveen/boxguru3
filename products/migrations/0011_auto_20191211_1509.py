# Generated by Django 2.2.6 on 2019-12-11 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20191211_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]