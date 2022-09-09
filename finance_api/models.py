from datetime import date
from django.db import models
from django.contrib.auth.models import User

class Contract(models.Model):
    class Frequency(models.TextChoices):
        MONTHLY = 'MONTHLY'
        QUARTERLY = 'QUARTERLY'
        ANNUALY = 'ANNUALY'

    name = models.CharField(max_length = 30)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "contracts")
    description = models.CharField(max_length = 300)
    first_billing_day = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    billing_frequency = models.CharField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )
    billing_amount = models.FloatField(null = True)