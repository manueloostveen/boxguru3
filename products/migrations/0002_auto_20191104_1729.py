# Generated by Django 2.2.6 on 2019-11-04 16:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='color',
            options={'ordering': ['color'], 'verbose_name': 'Color'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['product_type', 'inner_dim1'], 'permissions': (('can_see_all_liked_products', 'Get list of liked products'), ('create_update_delete', 'Create/update/delete products')), 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterModelOptions(
            name='producttype',
            options={'ordering': ['type'], 'verbose_name': 'Product type'},
        ),
        migrations.AlterModelOptions(
            name='wallthickness',
            options={'verbose_name': 'Wallthickness', 'verbose_name_plural': 'Wallthicknesses'},
        ),
        migrations.AddField(
            model_name='product',
            name='lowest_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=1000, null=True, verbose_name='Lowest price/box ex. BTW'),
        ),
        migrations.AddField(
            model_name='product',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Liked by'),
        ),
        migrations.AlterField(
            model_name='product',
            name='inner_dim1',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner width'),
        ),
        migrations.AlterField(
            model_name='product',
            name='inner_dim2',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner length'),
        ),
    ]