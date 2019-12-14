# Generated by Django 2.2.6 on 2019-11-04 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_maincategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttype',
            name='main_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.MainCategory'),
        ),
    ]