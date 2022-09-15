from datetime import date
from django.test import TestCase
from .models import Contract, User, Frequency

class ContractTestCase(TestCase):
    def test_contract(self):
        """Contract is created correctly with the default data"""
        User.objects.create(
            username = "Testing user"
        )
        Contract.objects.create(
            name = "Internet",
            description = "Internet bill",
            first_billing_day = date(year = 2022, month = 5, day = 20),
            user = User.objects.get(username="Testing user")
            )
        internet_contract = Contract.objects.get(name="Internet")
        self.assertEqual(internet_contract.end_date, None)
        self.assertEqual(internet_contract.billing_frequency, Frequency.MONTHLY)

    def test_archived(self):
        pass

    def test_compute_next_billing_day(self):
        pass

    def test_compute_previous_billing_day(self):
        pass

    def test_compute_amount_to_store(self):
        pass

    def test_compute_amount_to_store_regarding_first_day_of_month(self):
        pass



class SavingTestCase(TestCase):
    def test_saving(self):
        """Saving is created correctly with the default data"""
        pass

    def test_paid_out(self):
        pass


class RecurringSavingTestCase(TestCase):
    def test_recurring_saving(self):
        """Recurring Saving is created correctly with the default data"""
        pass

    def test_paid_out(self):
        pass

    def test_saved_amount(self):
        pass


class UserTestCase(TestCase):
    def test_beginning_of_current_month(self):
        pass

    def test_beginning_of_next_month(self):
        pass

    def test_create_statistics(self):
        pass
