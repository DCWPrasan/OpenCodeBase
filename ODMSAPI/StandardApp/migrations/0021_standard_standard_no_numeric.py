# Generated by Django 4.2.10 on 2024-06-03 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StandardApp', '0020_ipsstitle_title_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='standard',
            name='standard_no_numeric',
            field=models.BigIntegerField(db_index=True, null=True),
        ),
    ]
