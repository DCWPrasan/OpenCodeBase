# Generated by Django 4.2.10 on 2024-04-08 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DrawingApp', '0010_alter_drawing_date_of_registration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drawing',
            name='letter_number',
            field=models.CharField(max_length=250, null=True),
        ),
    ]