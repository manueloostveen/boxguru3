# Generated by Django 2.2.6 on 2019-11-04 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20191104_1905'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maincategory',
            options={'ordering': ['category'], 'verbose_name': 'Hoofdcategorie', 'verbose_name_plural': 'Hoofdcategoriën'},
        ),
    ]
