# Generated by Django 4.2.10 on 2024-05-28 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DrawingApp', '0017_alter_drawing_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='drawing',
            name='drawing_number_numeric',
            field=models.BigIntegerField(db_index=True, null=True),
        ),
    ]