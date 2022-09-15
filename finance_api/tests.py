from datetime import date
from django.test import TestCase
from .models import Contract, User, Frequency
from dateutil.relativedelta import relativedelta

class ContractTestCase(TestCase):
    @staticmethod
    def createSampleContract(
        pk,
        user,
        frequency = Frequency.MONTHLY,
        first_billing_day = date(2020, 1, 1),
        end_date = None,
        amount = 100
    ):
        return Contract.objects.create(
            pk = pk,
            name = f"contract_{pk}",
            description = f"{pk} contract description",
            billing_frequency = frequency,
            first_billing_day = first_billing_day,
            end_date = end_date,
            user = user,
            amount = amount
        )
    
    def setUp(cls):
        testing_user = User.objects.create(username = "Testing user")
        ContractTestCase.createSampleContract(1, testing_user, first_billing_day = date(2022, 5, 20))
        ContractTestCase.createSampleContract(2, testing_user, end_date = date.today() + relativedelta(months=1))
        ContractTestCase.createSampleContract(3, testing_user, end_date = date.today() - relativedelta(months=1))

    def test_contract(self):
        """Contract is created correctly with the default data"""
        first_contract = Contract.objects.get(pk=1)
        self.assertEqual(first_contract.end_date, None)
        self.assertEqual(first_contract.description, "1 contract description")
        self.assertEqual(first_contract.billing_frequency, Frequency.MONTHLY)
        self.assertEqual(first_contract.amount, 100)
        self.assertEqual(first_contract.user, User.objects.get(username = "Testing user"))
        self.assertEqual(first_contract.first_billing_day, date(2022, 5, 20))

        first_contract = Contract.objects.get(pk=2)
        self.assertEqual(first_contract.end_date, date.today() + relativedelta(months=1))

    def test_archived(self):
        """Archived method shows if contract ended in the past"""
        not_archived_contract = Contract.objects.get(pk=2)
        self.assertFalse(not_archived_contract.archived())

        archived_contract = Contract.objects.get(pk=3)
        self.assertTrue(archived_contract.archived())

    def test_compute_next_billing_day_frequency_monthly(self):
        """Next billing day for billing frequency: monthly is computed correctly based on the reference day"""
        contract = Contract.objects.get(pk=1)
        reference_day = date(2022, 6, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2022, 7, 20))

    def test_compute_next_billing_day_for_short_months_frequency_monthly(self):
        """Next billing day for billing frequency: monthly is set to last day of the month if the month is shorter than expected day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(4, testing_user, first_billing_day = date(2022, 1, 31))
        reference_day = date(2022, 2, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2022, 2, 28))

    def test_compute_previous_billing_day_frequency_monthly(self):
        """Previous billing day for billing frequency: monthly is computed correctly based on the reference day"""
        contract = Contract.objects.get(pk=1)
        reference_day = date(2022, 6, 21)
        self.assertEqual(contract.compute_previous_billing_day(reference_day), date(2022, 6, 20))

    def test_compute_next_billing_day_frequency_quarterly(self):
        """Next billing day for billing frequency: quarterly is computed correctly based on the reference day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(5, testing_user, first_billing_day = date(2022, 5, 20), frequency = Frequency.QUARTERLY)
        reference_day = date(2022, 6, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2022, 8, 20))

    def test_compute_next_billing_day_for_short_months_frequency_quarterly(self):
        """Next billing day for billing frequency: quarterly is set to last day of the month if the month is shorter than expected day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(4, testing_user, first_billing_day = date(2021, 11, 30), frequency = Frequency.QUARTERLY)
        reference_day = date(2021, 12, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2022, 2, 28))

    def test_compute_previous_billing_day_frequency_quarterly(self):
        """Previous billing day for billing frequency: quarterly is computed correctly based on the reference day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(5, testing_user, first_billing_day = date(2022, 5, 20), frequency = Frequency.QUARTERLY)
        reference_day = date(2022, 10, 21)
        self.assertEqual(contract.compute_previous_billing_day(reference_day), date(2022, 8, 20))

    def test_compute_next_billing_day_frequency_annually(self):
        """Next billing day for billing frequency: annually is computed correctly based on the reference day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(5, testing_user, first_billing_day = date(2022, 5, 20), frequency = Frequency.ANNUALY)
        reference_day = date(2022, 6, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2023, 5, 20))

    def test_compute_next_billing_day_for_short_months_frequency_annually(self):
        """Next billing day for billing frequency: annually is set to last day of the month if the month is shorter than expected day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(4, testing_user, first_billing_day = date(2020, 2, 29), frequency = Frequency.ANNUALY)
        reference_day = date(2020, 3, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2021, 2, 28))

    def test_compute_previous_billing_day_frequency_annually(self):
        """Previous billing day for billing frequency: annually is computed correctly based on the reference day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(5, testing_user, first_billing_day = date(2022, 5, 20), frequency = Frequency.ANNUALY)
        reference_day = date(2023, 12, 21)
        self.assertEqual(contract.compute_previous_billing_day(reference_day), date(2023, 5, 20))

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
