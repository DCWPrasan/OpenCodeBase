# Generated by Django 4.2.10 on 2024-06-13 10:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NoticeApp', '0007_rename_description_notice_notice_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newuserrequest',
            name='cost_code_department',
        ),
    ]