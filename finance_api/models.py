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


class Frequency(models.IntegerChoices):
    """
    Enum class used by Contract and RecurringSaving classes
    in order to define the billing frequency.
    """
    MONTHLY = 1
    QUARTERLY = 3
    ANNUALY = 12
    

class Contract(Cost):
    """
    Subclass of the Cost class that defines user specific contracts.

    Attributes:
        first_billing_day       Day when the contract started. Each next billing day is computed
                                based on this date.
        end_date                End date of the contract. None by default.
        billing_frequency       Defines billing frequency on the contract.
                                Can be one of the options defined in enum class Frequency:
                                Monthly, Quarterly, Annualy.
    """
    first_billing_day = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    billing_frequency = models.IntegerField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )

    def archived(self, reference_date = date.today()):
        """
        Returns boolean saying if the contract is archived,
        based on the end_date and reference_date.
        """
        return self.end_date < reference_date if self.end_date is not None else False

    def compute_next_billing_day(self, reference_date = date.today()):
        """
        Computes next billing day of the contract.
        Based on the first_billing_day, the function looks for the first possible billing day
        in the future (in relation to reference_date).
        """
        period_in_months = self.billing_frequency
        billing_day = self.first_billing_day
        while billing_day <= reference_date:
                billing_day = billing_day + relativedelta(months=+period_in_months)

        if self.end_date is not None and self.end_date < billing_day:
            return None
            
        return billing_day

    def compute_previous_billing_day(self, reference_date = date.today()):
        """
        Computes previous billing day of the contract.
        Based on the first_billing_day, the function looks for the last billing day
        in the past (in relation to reference_date).
        """
        period_in_months = self.billing_frequency
        previous_billing = self.compute_next_billing_day(reference_date) - relativedelta(months=+period_in_months)
        return previous_billing

    def compute_amount_to_store(self, reference_date = date.today()):

        period_in_months = self.billing_frequency
        monthly_store = self.amount / period_in_months
        next_billing = self.compute_next_billing_day(reference_date)
        full_remaining_months = relativedelta(next_billing, reference_date).months
        to_store = monthly_store * (period_in_months - full_remaining_months)
        return to_store


    def compute_amount_to_store_regarding_first_day_of_month(self, reference_date = date.today()):
        """
        Computes amount that needs to be stored for the contract.

        The computed value is based on the following factors:
        - user specific first_day_of_the_month 
        - reference_date (date.today() by default)
        - billing_frequency of the contract
        - contract's amount

        Basically, the functions checks how many times new month will begin
        until the next expected billing day,
        meaning how many salaries the user will get.
        Then, it computes which part of the full contract amount should be stored
        at this point of time.

        E.g. having a contract with next billing day 12.12.2022 and billing frequency: QUARTERLY
        for a user with first_day_of_the_month = 5.

        * reference_date since 1.10.2022 until 4.10.2022:
        - there will be 3 salaries until billing day: 5.10.2022, 5.11.2022 and 5.12.2022.
        Therefore 0% of the amount needs to be stored.

        * reference_date since 5.10.2022 until 4.11.2022:
        - there will be 2 additional salaries until billing day: 5.11.2022 and 5.12.2022.
        Therefore 1/3 of the amount needs to be stored.

        * reference_date since 5.11.2022 until 4.12.2022:
        - there will be 1 additional salary until billing day: 5.12.2022.
        Therefore 2/3 of the amount needs to be stored.

        * reference_date since 4.12.2022 until 11.12.2022:
        - there will be no additional salary until billing day.
        Therefore 100% of the amount needs to be stored.

        The amount_to_store is computed analogically for billing_frequency MONTHLY and ANNUALY,
        with the difference that for the MONTHLY billed contracts the stored amount can be
        either 0 or 100% (because there is always max. 1 salary until the billing_day)
        and for ANUALLY contracts the program computes 1/12 of the full amount
        for each month to store.
        """
        next_month_first_day = self.user.beginning_of_next_month(reference_date)
        next_billing = self.compute_next_billing_day(reference_date)

        beginnings_until_next_billinng = 0

        while next_month_first_day < next_billing:
            beginnings_until_next_billinng += 1
            next_month_first_day += relativedelta(months=1)

        if beginnings_until_next_billinng == 0:
            return self.amount

        period_in_months = self.billing_frequency

        if period_in_months - beginnings_until_next_billinng == 0:
            return 0

        monthly_store = self.amount / period_in_months
        to_store = monthly_store * (period_in_months - beginnings_until_next_billinng)
        return to_store


class Saving(Cost):
    """
    Subclass of the Cost class that defines user specific one-time saving.

    Attributes:
        pay_out_day       Day when the saved amount should be paid out.
    """
    pay_out_day = models.DateField(null = True)

    def paid_out(self, reference_date = date.today()):
        """
        Returns boolean saying if the saved amount has been paid out,
        based on the pay_out_day and reference_date.
        """
        return self.pay_out_day <= reference_date if self.pay_out_day is not None else False



class RecurringSaving(Cost):
    """
    Subclass of the Cost class that defines user specific recurring saving.

    Attributes:
        start_date      Day when the saving programm started.
        end_date        End date of the saving.
                        From this day on, no further amounts will be saved.
        pay_out_day     Day when the total saved amount should be paid out. 
        frequency       Defines frequency on the saving recurrency.
                        Can be one of the options defined in enum class Frequency:
                        Monthly, Quarterly, Annualy.
    """

    start_date = models.DateField(default = date.today)
    end_date = models.DateField(null = True)
    pay_out_day = models.DateField(null = True)
    frequency = models.IntegerField(
        max_length = 10,
        choices = Frequency.choices,
        default = Frequency.MONTHLY
    )

    def paid_out(self, reference_date = date.today()):
        """
        Returns boolean saying if the saved amount has been paid out,
        based on the pay_out_day and reference_date.
        """
        return self.pay_out_day < reference_date if self.pay_out_day is not None else False

    def saved_amount(self, reference_date):
        """
        Computes total amount saved for this saving,
        based on the start_date, reference_date, recurrency and amount.
        """
        if self.paid_out(reference_date):
            return 0

        save_day = self.start_date
        end_day = self.end_date if self.end_date is not None and self.end_date < reference_date else reference_date
        total_saved = 0
        saving_period = self.frequency
        while save_day <= end_day:
            total_saved += self.amount
            save_day = save_day + relativedelta(months=+saving_period)
        return total_saved