# Generated by Django 4.2.10 on 2024-04-08 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DrawingApp', '0008_drawing_fdr_approve_date_drawing_letter_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drawing',
            name='letter_date',
        ),
        migrations.RemoveField(
            model_name='drawing',
            name='supplier_number',
        ),
    ]
