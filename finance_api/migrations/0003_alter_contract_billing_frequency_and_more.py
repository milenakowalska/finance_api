# Generated by Django 4.0.6 on 2022-09-17 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance_api', '0002_saving_recurringsaving_contract'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='billing_frequency',
            field=models.CharField(choices=[(1, 'Monthly'), (3, 'Quarterly'), (12, 'Annualy')], default=1, max_length=10),
        ),
        migrations.AlterField(
            model_name='contract',
            name='description',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='recurringsaving',
            name='description',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='recurringsaving',
            name='frequency',
            field=models.CharField(choices=[(1, 'Monthly'), (3, 'Quarterly'), (12, 'Annualy')], default=1, max_length=10),
        ),
        migrations.AlterField(
            model_name='saving',
            name='description',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
