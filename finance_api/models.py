from datetime import date
from django.db import models
from django.contrib.auth.models import User


class Cost(models.Model):
    name = models.CharField(max_length = 30)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "%(class)s")
    description = models.CharField(max_length = 300)
    amount = models.FloatField(null = True)

    class Meta:
        abstract = True


class Frequency(models.TextChoices):
        MONTHLY = 'MONTHLY'
        QUARTERLY = 'QUARTERLY'
        ANNUALY = 'ANNUALY'


class Contract(Cost):
    first_billing_day = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    billing_frequency = models.CharField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )


class Saving(Cost):
    pay_out_day = models.DateField(null = True)


class RecurringSaving(Cost):
    start_date = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    billing_frequency = models.CharField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )

