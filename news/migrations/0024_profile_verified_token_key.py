# Generated by Django 3.0.5 on 2020-06-21 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0023_profile_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='verified_token_key',
            field=models.CharField(default='JKKQWKZITG', max_length=10),
        ),
    ]
