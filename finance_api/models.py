from datetime import date
from django.db import models
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta

class Cost(models.Model):
    name = models.CharField(max_length = 30)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "%(class)s")
    description = models.CharField(max_length = 300)
    amount = models.FloatField(default=0)

    class Meta:
        abstract = True


class Frequency(models.TextChoices):
    MONTHLY = 'MONTHLY'
    QUARTERLY = 'QUARTERLY'
    ANNUALY = 'ANNUALY'

    @staticmethod
    def frequency_to_months(frequency):
        return 1 if frequency == Frequency.MONTHLY else 3 if frequency == Frequency.QUARTERLY else 12


class Contract(Cost):
    first_billing_day = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    billing_frequency = models.CharField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )

    def archived(self):
        return self.end_date < date.today() if self.end_date is not None else False

    def compute_next_billing_day(self, reference_date = date.today()):
        period_in_months = Frequency.frequency_to_months(self.billing_frequency)
        billing_day = self.first_billing_day
        while billing_day < reference_date:
                billing_day = billing_day + relativedelta(months=+period_in_months)

        return billing_day

    def compute_amount_to_store(self, reference_date = date.today()):
        period_in_months = Frequency.frequency_to_months(self.billing_frequency)
        monthly_store = self.amount / period_in_months
        next_billing = self.compute_next_billing_day(reference_date)
        full_remaining_months = relativedelta(next_billing, reference_date).months
        to_store = monthly_store * (period_in_months - full_remaining_months)
        return to_store

    """
    10.03 - Quarterly, 2100 EUR
    3 minus:
    - 2 months x days -> 33%
    - 1 month x days -> 66%
    - 0 months x days -> 100%
    10.06

    10.03.2022 - Annually, 12000 EUR
    12 minus:
    - 11 months -> 1/12 * amount
    - 10 months -> 1/12 * amount * 2
    - 2 months x days -> 33%
    - 1 month x days -> 66%
    - 0 months x days -> 100%
    10.03.2023
    """

class Saving(Cost):
    pay_out_day = models.DateField(null = True)

    def paid_out(self):
        return self.pay_out_day < date.today() if self.pay_out_day is not None else False



class RecurringSaving(Cost):
    start_date = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    pay_out_day = models.DateField(null = True)
    frequency = models.CharField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )

    def paid_out(self):
        return self.pay_out_day < date.today() if self.pay_out_day is not None else False

    def saved_amount(self, reference_date):
        save_day = self.start_date
        end_day = self.end_date if self.end_date is not None and self.end_date < reference_date else reference_date
        total_saved = 0
        saving_period = Frequency.frequency_to_months(self.frequency)
        while save_day <= end_day:
            total_saved += self.amount
            save_day = save_day + relativedelta(months=+saving_period)
        return total_saved