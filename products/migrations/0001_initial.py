# Generated by Django 3.0.3 on 2020-02-25 11:48

import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        HStoreExtension(),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=120, null=True, verbose_name='Color')),
            ],
            options={
                'verbose_name': 'Color',
                'ordering': ['color'],
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=120, verbose_name='Company')),
            ],
            options={
                'ordering': ['company'],
            },
        ),
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=120, null=True, verbose_name='Hoofdcategorie')),
                ('category_id', models.IntegerField(blank=True, verbose_name='Category id')),
                ('category_url', models.CharField(max_length=120, null=True, verbose_name='URL-naam')),
            ],
            options={
                'verbose_name': 'Hoofdcategorie',
                'verbose_name_plural': 'Hoofdcategoriën',
                'ordering': ['category'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inner_dim1', models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner width')),
                ('inner_dim2', models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner length')),
                ('inner_dim3', models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner height')),
                ('outer_dim1', models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer width')),
                ('outer_dim2', models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer length')),
                ('outer_dim3', models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer height')),
                ('volume', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='Volume')),
                ('inner_variable_dimension_MIN', models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner variable dimension min')),
                ('inner_variable_dimension_MAX', models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner variable dimension max')),
                ('outer_variable_dimension_MIN', models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer variable dimension min')),
                ('outer_variable_dimension_MAX', models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer variable dimension max')),
                ('variable_height', models.BooleanField(blank=True, null=True)),
                ('height_sorter', models.PositiveIntegerField(blank=True, null=True, verbose_name='Sortable height')),
                ('diameter', models.PositiveIntegerField(blank=True, null=True, verbose_name='Diameter')),
                ('bottles', models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of bottles')),
                ('standard_size', models.CharField(blank=True, max_length=5, null=True, verbose_name='Standard size')),
                ('description', models.CharField(blank=True, default='', max_length=120, verbose_name='Product description')),
                ('in_stock', models.BooleanField(blank=True, null=True)),
                ('url', models.URLField(blank=True, max_length=120, verbose_name='URL')),
                ('price_ex_BTW', models.DecimalField(decimal_places=2, max_digits=1000, verbose_name='Price/box ex. BTW')),
                ('price_incl_BTW', models.DecimalField(decimal_places=2, max_digits=1000, verbose_name='Price/box incl. BTW')),
                ('minimum_purchase', models.PositiveIntegerField(blank=True, null=True, verbose_name='Bundle size')),
                ('price_table', django.contrib.postgres.fields.hstore.HStoreField()),
                ('lowest_price', models.DecimalField(blank=True, decimal_places=2, max_digits=1000, null=True, verbose_name='Lowest price/box ex. BTW')),
                ('product_image', models.CharField(blank=True, max_length=200, null=True)),
                ('color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.Color', verbose_name='Color')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Company')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['inner_dim1'],
                'permissions': (('can_see_all_liked_products', 'Get list of liked products'), ('create_update_delete', 'Create/update/delete products')),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=120, verbose_name='Tag')),
            ],
            options={
                'ordering': ['tag'],
            },
        ),
        migrations.CreateModel(
            name='TierPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tier', models.PositiveIntegerField(verbose_name='Tier')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price/box ex. BTW')),
            ],
        ),
        migrations.CreateModel(
            name='WallThickness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wall_thickness', models.CharField(max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Wallthickness',
                'verbose_name_plural': 'Wallthicknesses',
            },
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manyfield', models.ManyToManyField(to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=120, verbose_name='Product Type')),
                ('type_singular', models.CharField(blank=True, max_length=120, null=True, verbose_name='Product Type Singular')),
                ('product_type_id', models.IntegerField(blank=True)),
                ('main_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.MainCategory')),
            ],
            options={
                'verbose_name': 'Product type',
                'ordering': ['type'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.ProductType', verbose_name='Product type'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(to='products.Tag'),
        ),
    ]
