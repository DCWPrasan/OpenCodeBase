# Generated by Django 4.2.10 on 2024-04-08 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DrawingApp', '0011_alter_drawing_letter_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='drawing',
            old_name='fdr_approve_date',
            new_name='fdr_approved_date',
        ),
    ]
