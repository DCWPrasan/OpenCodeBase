# Generated by Django 4.2.10 on 2024-04-06 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AuthApp', '0005_user_is_view_layout'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_view_manual',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_view_standard',
            field=models.BooleanField(default=True),
        ),
    ]
