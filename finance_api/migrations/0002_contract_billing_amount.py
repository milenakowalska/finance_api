# Generated by Django 4.0.6 on 2022-09-09 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='billing_amount',
            field=models.FloatField(null=True),
        ),
    ]
