# Generated by Django 4.0.6 on 2022-09-12 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance_api', '0008_contract_archived_recurringsaving_archived_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='archived',
        ),
        migrations.RemoveField(
            model_name='recurringsaving',
            name='archived',
        ),
        migrations.RemoveField(
            model_name='saving',
            name='archived',
        ),
    ]
