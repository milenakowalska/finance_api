# Generated by Django 4.0.6 on 2022-09-14 19:19

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Saving',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=300)),
                ('amount', models.FloatField(default=0)),
                ('pay_out_day', models.DateField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecurringSaving',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=300)),
                ('amount', models.FloatField(default=0)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField(null=True)),
                ('pay_out_day', models.DateField(null=True)),
                ('frequency', models.CharField(choices=[('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('ANNUALY', 'Annualy')], default='MONTHLY', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=300)),
                ('amount', models.FloatField(default=0)),
                ('first_billing_day', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField(null=True)),
                ('billing_frequency', models.CharField(choices=[('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('ANNUALY', 'Annualy')], default='MONTHLY', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
