# Generated by Django 4.2.10 on 2024-04-23 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AuthApp', '0007_alter_subvolume_sub_volume_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_disable_dwg_file',
            field=models.BooleanField(default=True),
        ),
    ]