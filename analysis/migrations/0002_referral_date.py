# Generated by Django 3.0.3 on 2020-03-12 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='referral',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
