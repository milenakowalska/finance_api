# Generated by Django 4.0.6 on 2022-09-17 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance_api', '0003_alter_contract_billing_frequency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='billing_frequency',
            field=models.CharField(choices=[('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('ANNUALY', 'Annualy')], default='MONTHLY', max_length=10),
        ),
        migrations.AlterField(
            model_name='recurringsaving',
            name='frequency',
            field=models.CharField(choices=[('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('ANNUALY', 'Annualy')], default='MONTHLY', max_length=10),
        ),
    ]
