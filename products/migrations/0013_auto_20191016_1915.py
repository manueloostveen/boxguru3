# Generated by Django 2.2.6 on 2019-10-16 19:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_auto_20191016_1841'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='inner_var_dim_MAX',
            new_name='inner_variable_dimension_MAX',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='inner_var_dim_MIN',
            new_name='inner_variable_dimension_MIN',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='outer_var_dim_MAX',
            new_name='outer_variable_dimension_MAX',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='outer_var_dim_MIN',
            new_name='outer_variable_dimension_MIN',
        ),
    ]
