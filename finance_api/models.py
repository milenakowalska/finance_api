from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from dateutil.relativedelta import relativedelta
from django.core.validators import MaxValueValidator, MinValueValidator
import calendar
from .utils import StatisticContract, StatisticSaving, Statistics


class User(AbstractUser):
    """
    Custom authentication User model.

    Additional attribute:
        first_day_of_the_month      Day of the month that points out when the calculation period for the user should begin.
                                    It is recommended to match the day of the salary,
                                    so that the program computes disponible amount in statistics is according to truth.
                                    By default the day points out to the actual beginning of the month (day 1).
    """

    first_day_of_the_month = models.IntegerField(default = 1, validators=[
            MaxValueValidator(31),
            MinValueValidator(1)
    ])

    def beginning_of_current_month(self, reference_date = date.today()):
        """
        Calculates the beginning of the month based on the reference_date
        and the user specific first_day_of_the_month.

        If first_day_of_the_month is bigger than the last day of the month,
        the function returns last applicable day.

        e.g.
        first_day_of_the_month = 31
        reference_date = date(2022, 2, 1)
        result = date(2022, 2, 28)
        """
        last_day_of_month = calendar.monthrange(reference_date.year, reference_date.month)[1]

        if last_day_of_month < self.first_day_of_the_month:
            first_day = date(reference_date.year, reference_date.month, last_day_of_month)
        else:
            first_day = date(reference_date.year, reference_date.month, self.first_day_of_the_month)
          
        if first_day > reference_date:
            first_day = first_day - relativedelta(months=1)

        return first_day
    
    def beginning_of_next_month(self, reference_date = date.today()):
        """
        Calculates the beginning of the next month based on the reference_date
        and the user specific first_day_of_the_month.

        If first_day_of_the_month is bigger than the last day of the next month,
        the function returns last applicable day.
        """
        try:
            first_day = date(reference_date.year, reference_date.month, self.first_day_of_the_month)
        except ValueError:
            last_day_of_month = calendar.monthrange(reference_date.year, reference_date.month)[1]
            first_day = date(reference_date.year, reference_date.month, last_day_of_month)
        
        if first_day <= reference_date:
            first_day = first_day + relativedelta(months=1)

        return first_day

    def create_statistics(self, balance, reference_date):
        """
        Creates statistics
        based on:
        - balance (should illustrate total account balance)
        - contracts, savings and recurring savings of the user
        - reference_date

        The function computes, which amount should be stored 
        for the specific contract and saving
        and subtracts this amount from the given balance,
        in order to compute the amount disponible for the user.

        The result is presented as an instance of the class utils.Statistics.
        """
        all_savings = []
        active_contracts = []
        user_contracts = self.contract.all()
        user_savings = self.saving.all()
        user_recurring_savings = self.recurringsaving.all()

        for saving in user_savings:
            if not saving.paid_out(reference_date):
                all_savings.append(StatisticSaving(saving.name, False, saving.amount))
                balance -= saving.amount

        for recurring_saving in user_recurring_savings:
            if not recurring_saving.paid_out(reference_date):
                total_saved = recurring_saving.saved_amount(reference_date)
                all_savings.append(StatisticSaving(recurring_saving.name, True, total_saved))
                balance -= total_saved

        for contract in user_contracts:
            if not contract.archived():
                billing_day = contract.compute_next_billing_day(reference_date)
                to_store = contract.compute_amount_to_store_regarding_first_day_of_month(reference_date)

                active_contracts.append(StatisticContract(contract.name, billing_day, contract.amount, to_store))
                balance -= to_store

        return Statistics(balance, all_savings, active_contracts)


class Cost(models.Model):
    """
    Abstract class used as a base to model user related costs.
    Currently used to model Contract, Saving and RecurringSaving.

    Attributes:
        name            Name of the costs
        user            Foreign key pointing to the user that this costs is related to
        description     Optional description.
        amount          Amount of money related to this costs.
    """
    name = models.CharField(max_length = 30)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "%(class)s")
    description = models.CharField(max_length = 300, null = True)
    amount = models.FloatField(default=0)

    class Meta:
        # mark model as abstract,
        # so that it is not used to create any database table
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

    def archived(self, reference_date = date.today()):
        return self.end_date < reference_date if self.end_date is not None else False

    def compute_next_billing_day(self, reference_date = date.today()):
        period_in_months = Frequency.frequency_to_months(self.billing_frequency)
        billing_day = self.first_billing_day
        while billing_day <= reference_date:
                billing_day = billing_day + relativedelta(months=+period_in_months)

        if self.end_date is not None and self.end_date < billing_day:
            return None
            
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

        beginnings_until_next_billinng = 0

        while next_month_first_day < next_billing:
            beginnings_until_next_billinng += 1
            next_month_first_day += relativedelta(months=1)

        if beginnings_until_next_billinng == 0:
            return self.amount

        period_in_months = Frequency.frequency_to_months(self.billing_frequency)

        if period_in_months - beginnings_until_next_billinng == 0:
            return 0

        monthly_store = self.amount / period_in_months
        to_store = monthly_store * (period_in_months - beginnings_until_next_billinng)
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

    def paid_out(self, reference_date = date.today()):
        return self.pay_out_day <= reference_date if self.pay_out_day is not None else False



class RecurringSaving(Cost):
    start_date = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    pay_out_day = models.DateField(null = True)
    frequency = models.CharField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )

    def paid_out(self, reference_date = date.today()):
        return self.pay_out_day < reference_date if self.pay_out_day is not None else False

    def saved_amount(self, reference_date):
        if self.paid_out(reference_date):
            return 0

        save_day = self.start_date
        end_day = self.end_date if self.end_date is not None and self.end_date < reference_date else reference_date
        total_saved = 0
        saving_period = Frequency.frequency_to_months(self.frequency)
        while save_day <= end_day:
            total_saved += self.amount
            save_day = save_day + relativedelta(months=+saving_period)
        return total_saved