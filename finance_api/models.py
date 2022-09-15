from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from dateutil.relativedelta import relativedelta
from django.core.validators import MaxValueValidator, MinValueValidator
import calendar
from .utils import StatisticContract, StatisticSaving, Statistics

class User(AbstractUser):
    first_day_of_the_month = models.IntegerField(default = 1, validators=[
            MaxValueValidator(31),
            MinValueValidator(1)
    ])

    def beginning_of_current_month(self, reference_date = date.today()):
        try:
            first_day = date(reference_date.year, reference_date.month, self.first_day_of_the_month)
            return first_day
        except ValueError:
            last_day_of_month = calendar.monthrange(reference_date.year, reference_date.month)[1]
            first_day = date(reference_date.year, reference_date.month, last_day_of_month)
            return first_day

    def beginning_of_next_month(self, reference_date = date.today()):
        return self.beginning_of_current_month(reference_date) + relativedelta(months=1)

    def create_statistics(self, balance, reference_date):
        all_savings = []
        active_contracts = []
        user_contracts = self.contracts
        user_savings = self.savings
        user_recurring_savings = self.recurringsavings

        for saving in user_savings:
            if not saving.paid_out():
                all_savings.append(StatisticSaving(saving.name, False, saving.amount))
                balance -= saving.amount

        for recurring_saving in user_recurring_savings:
            if not recurring_saving.paid_out():
                total_saved = recurring_saving.saved_amount(reference_date)
                all_savings.append(StatisticSaving(recurring_saving.name, True, total_saved))
                balance -= recurring_saving.amount

        for contract in user_contracts:
            if not contract.archived():
                billing_day = contract.compute_next_billing_day(reference_date)
                to_store = contract.compute_amount_to_store_regarding_first_day_of_month(reference_date)

                active_contracts.append(StatisticContract(contract.name, billing_day, contract.amount, to_store))
                balance -= to_store

        return Statistics(balance, all_savings, active_contracts)

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

    def compute_previous_billing_day(self, reference_date = date.today()):
        period_in_months = Frequency.frequency_to_months(self.billing_frequency)
        previous_billing = self.compute_next_billing_day(reference_date) - relativedelta(months=+period_in_months)
        return previous_billing

    def compute_amount_to_store(self, reference_date = date.today()):
        period_in_months = Frequency.frequency_to_months(self.billing_frequency)
        monthly_store = self.amount / period_in_months
        next_billing = self.compute_next_billing_day(reference_date)
        full_remaining_months = relativedelta(next_billing, reference_date).months
        to_store = monthly_store * (period_in_months - full_remaining_months)
        return to_store

    """ 
    less than month until next_bill && next_bill < beginning_of_next_month: 100%
    less than month after previous_bill && beginning_of_previous_month < previous_bill < beginning_of_next_month - 0%

    in other cases:
        monthly_store * (period_in_months - full_remaining_months)
    """
    def compute_amount_to_store_regarding_first_day_of_month(self, reference_date = date.today()):
        current_month_first_day = self.user.beginning_of_current_month(reference_date)
        next_month_first_day = self.user.beginning_of_next_month(reference_date)
        previous_billing = self.compute_previous_billing_day(reference_date)
        next_billing = self.compute_next_billing_day(reference_date)

        less_than_month_until_next_bill = relativedelta(next_billing, reference_date).months < 1
        less_than_month_after_previous_bill = relativedelta(reference_date, previous_billing).months < 1
        if less_than_month_until_next_bill and next_billing < next_month_first_day:
            return self.amount
        elif less_than_month_after_previous_bill and current_month_first_day < previous_billing:
            return 0

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

    10.03 - billing
    10.06 - billing
    10.09 - billing

    5 - beginning of the month
    5.03-10.03 -> store 100%
    10.03-5.04 -> store 0
    5.04-5.05 -> store 33%
    5.05-5.06 -> store 66%
    5.06-10.06 -> store 100%

    period_in_months = 3
    monthly_store = 700 EUR
    next_billing = 10.06

    8.03:
    beginning_of_current_month 5.03
    beginning_of_next_month 5.04
----
    frequency: monthly:
    billing_day: 20.03
    8.03 - bis billing_day -> 100%
    21.03 - nach billing_day -> 0
----
    frequency: quarterly:
    billing_day: 20.03, until then: 0 full months
    bis billing_day -> 100%
    nach billing_day -> 0    

    billing_day: 20.04, until then: 1 full month
    bis beginning_of_next_month -> 66%
    nach beginning_of_next_month -> 100%

    billing_day: 20.05, until then: 2 full months
    bis beginning_of_next_month -> 33%
    nach beginning_of_next_month -> 66%

-----
    frequency: yearly:
    billing_day: 20.03
    bis billing_day -> 100%
    nach billing_day -> 0    

    billing_day: 20.04
    bis beginning_of_next_month -> 11/12
    nach beginning_of_next_month -> 12/12

    billing_day: 20.05
    bis beginning_of_next_month -> 10/12
    nach beginning_of_next_month -> 12/12

----
    less than month until next_bill && next_bill < beginning_of_next_month: 100%
    less than month after previous_bill && beginning_of_previous_month < previous_bill < beginning_of_next_month - 100%

    in other cases:
        monthly_store * (period_in_months - full_remaining_months)

    15 - beginning of the month
    15.02-10.03 -> store 100%
    10.03-15.03 -> store 0
    15.03-15.04 -> store 33%
    15.04-15.05 -> store 66%
    15.05-10.06 -> store 100%

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