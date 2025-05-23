# Generated by Django 4.1.7 on 2025-02-18 12:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Barcodes',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('barcode_no', models.CharField(max_length=250, null=True)),
                ('is_product_type', models.BooleanField(default=True)),
                ('status', models.CharField(default='Used', max_length=6)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='BorrowedStock',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('net_quantity', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Employees',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('personnel_number', models.CharField(max_length=240)),
                ('name', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=10, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=235)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=250)),
                ('ucs_code', models.CharField(db_index=True, max_length=250, unique=True)),
                ('description', models.TextField(null=True)),
                ('description_sap', models.TextField(null=True)),
                ('min_threshold', models.IntegerField()),
                ('max_threshold', models.IntegerField(null=True)),
                ('net_quantity', models.FloatField(default=0)),
                ('price', models.FloatField(default=0)),
                ('is_mutli_type_unit', models.BooleanField(default=False)),
                ('ved_category', models.CharField(choices=[('Vital', 'VITAL'), ('Essential', 'ESSENTIAL'), ('Desirable', 'DESIRABLE')], default='Vital', max_length=20)),
                ('lead_time', models.IntegerField(default=1, help_text='Lead time in days')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Racks',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('rack_no', models.CharField(max_length=120)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=235)),
                ('is_central_store', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Stocks',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('quantity', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=235)),
            ],
        ),
        migrations.CreateModel(
            name='StocksHistory',
            fields=[
                ('id', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False)),
                ('history_type', models.CharField(choices=[('NEW MATERIAL', 'NEW MATERIAL'), ('RETURN MATERIAL', 'RETURN MATERIAL'), ('BORROWING MATERIAL', 'BORROWING MATERIAL'), ('RETURN BORROWED MATERIAL', 'RETURN BORROWED MATERIAL'), ('MATERIAL CONSUMPTION', 'MATERIAL CONSUMPTION')], default='NEW MATERIAL', max_length=30)),
                ('purpose', models.TextField(null=True)),
                ('quantity', models.FloatField(default=0)),
                ('product_quantity', models.FloatField(default=0)),
                ('is_stock_out', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='AdminApp.employees')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AdminApp.stocks')),
            ],
        ),
    ]
