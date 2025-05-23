# Generated by Django 4.1.7 on 2025-02-26 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0004_rename_net_quantity_borrowedstock_borrowed_quantity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borrowedstock',
            name='is_lent',
        ),
        migrations.AlterField(
            model_name='stockshistory',
            name='history_type',
            field=models.CharField(choices=[('NEW MATERIAL', 'NEW MATERIAL'), ('RETURN MATERIAL', 'RETURN MATERIAL'), ('RECEIVE LENT MATERIAL', 'RECEIVE LENT MATERIAL'), ('BORROWING MATERIAL', 'BORROWING MATERIAL'), ('RETURN BORROWED MATERIAL', 'RETURN BORROWED MATERIAL'), ('MATERIAL CONSUMPTION', 'MATERIAL CONSUMPTION'), ('LENDING MATERIAL', 'LENDING MATERIAL')], db_index=True, default='NEW MATERIAL', max_length=30),
        ),
    ]
