# Generated by Django 4.2.10 on 2024-04-11 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DrawingApp', '0013_alter_drawing_drawing_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drawinglog',
            name='status',
            field=models.CharField(choices=[('View Drawing', 'VIEW'), ('Add Drawing', 'ADD'), ('Update Drawing', 'UPDATE'), ('Archive Drawing', 'ARCHIVE'), ('Delete Drawing', 'DELETE'), ('Download Drawing', 'DOWNLOAD')], default='View Drawing', max_length=20),
        ),
    ]
