# Generated by Django 4.2.10 on 2024-04-05 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StandardApp', '0004_alter_rsngroup_group_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rsngroup',
            name='group_no',
            field=models.CharField(max_length=100, null=True),
        ),
    ]