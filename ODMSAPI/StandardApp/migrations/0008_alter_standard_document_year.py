# Generated by Django 4.2.10 on 2024-04-06 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StandardApp', '0007_ipsstitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standard',
            name='document_year',
            field=models.CharField(max_length=10, null=True),
        ),
    ]