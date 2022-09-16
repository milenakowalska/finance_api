from datetime import date
from django.test import TestCase
from .models import Contract, User, Frequency, Saving, RecurringSaving
from dateutil.relativedelta import relativedelta
from .utils import StatisticContract, StatisticSaving, Statistics

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
    
    def setUp(self):
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
        contract = ContractTestCase.createSampleContract(6, testing_user, first_billing_day = date(2021, 11, 30), frequency = Frequency.QUARTERLY)
        reference_day = date(2021, 12, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2022, 2, 28))

    def test_compute_previous_billing_day_frequency_quarterly(self):
        """Previous billing day for billing frequency: quarterly is computed correctly based on the reference day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(7, testing_user, first_billing_day = date(2022, 5, 20), frequency = Frequency.QUARTERLY)
        reference_day = date(2022, 10, 21)
        self.assertEqual(contract.compute_previous_billing_day(reference_day), date(2022, 8, 20))

    def test_compute_next_billing_day_frequency_annually(self):
        """Next billing day for billing frequency: annually is computed correctly based on the reference day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(8, testing_user, first_billing_day = date(2022, 5, 20), frequency = Frequency.ANNUALY)
        reference_day = date(2022, 6, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2023, 5, 20))

    def test_compute_next_billing_day_for_short_months_frequency_annually(self):
        """Next billing day for billing frequency: annually is set to last day of the month if the month is shorter than expected day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(9, testing_user, first_billing_day = date(2020, 2, 29), frequency = Frequency.ANNUALY)
        reference_day = date(2020, 3, 21)
        self.assertEqual(contract.compute_next_billing_day(reference_day), date(2021, 2, 28))

    def test_compute_previous_billing_day_frequency_annually(self):
        """Previous billing day for billing frequency: annually is computed correctly based on the reference day"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(10, testing_user, first_billing_day = date(2022, 5, 20), frequency = Frequency.ANNUALY)
        reference_day = date(2023, 12, 21)
        self.assertEqual(contract.compute_previous_billing_day(reference_day), date(2023, 5, 20))

    def test_next_billing_day_with_end_date(self):
        """Next billing day returns None if contract end_date is before"""
        testing_user = User.objects.get(username = "Testing user")
        contract = ContractTestCase.createSampleContract(11, testing_user, first_billing_day = date(2022, 5, 20), end_date = date(2022, 10, 2))
        reference_day = date(2022, 9, 30)
        self.assertEqual(contract.compute_next_billing_day(reference_day), None)

    def test_compute_amount_to_store_monthly(self):
        """Amount to store for billing frequency: monthy equals: 
        - 100% if billing_day comes sooner than beginning of next month
        - 0 if beginning of next month comes sooner than billing_day
        """
        testing_user_day_10 = User.objects.create(username = "User_10", first_day_of_the_month = 10)
        contract = ContractTestCase.createSampleContract(11, testing_user_day_10, first_billing_day = date(2022, 5, 20), amount = 100)

        reference_day = date(2022, 6, 30)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 0)
        reference_day = date(2022, 7, 10)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 100)

        testing_user_day_25 = User.objects.create(username = "User_25", first_day_of_the_month = 25)
        contract = ContractTestCase.createSampleContract(12, testing_user_day_25, first_billing_day = date(2022, 5, 20), amount = 100)
        reference_day = date(2022, 6, 22)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 0)
        reference_day = date(2022, 6, 25)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 100)

    def test_compute_amount_to_store_quarterly(self):
        """Amount to store for billing frequency: quarterly equals: 
        - 100% if no more beginning of the month until next_bill_day left
        - 66% if 1 more beginning of the month until next_bill_day left
        - 33% if 2 more beginnings of the month until next_bill_day left
        - 0 if 3 more beginnings of the month until next_bill_day left
        """
        testing_user_day_10 = User.objects.create(username = "User_10", first_day_of_the_month = 10)
        contract = ContractTestCase.createSampleContract(11, testing_user_day_10, first_billing_day = date(2022, 5, 20), amount = 300, frequency=Frequency.QUARTERLY)

        reference_day = date(2022, 8, 21)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 0)
        reference_day = date(2022, 9, 9)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 0)
        reference_day = date(2022, 9, 10)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 100)
        reference_day = date(2022, 10, 9)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 100)
        reference_day = date(2022, 10, 10)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 200)
        reference_day = date(2022, 11, 9)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 200)
        reference_day = date(2022, 11, 10)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 300)
        reference_day = date(2022, 11, 19)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 300)
        reference_day = date(2022, 11, 20)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 0)

    def test_compute_amount_to_store_annually(self):
        """Amount to store for billing frequency: annually equals: 
        - 100% if no more beginning of the month until next_bill_day left
        - 0 if 12 more beginnings of the month until next_bill_day left
        - 100% * (12-x)/12 where x is the amount of new months until next bill
        """
        testing_user_day_10 = User.objects.create(username = "User_10", first_day_of_the_month = 10)
        contract = ContractTestCase.createSampleContract(
            12,
            testing_user_day_10,
            first_billing_day = date(2022, 5, 20),
            amount = 1200,
            frequency=Frequency.ANNUALY
        )

        reference_day = date(2022, 5, 21)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 0)
        reference_day = date(2022, 6, 20)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 100)
        reference_day = date(2022, 9, 9)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 300)
        reference_day = date(2022, 9, 10)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 400)
        reference_day = date(2023, 4, 10)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 1100)
        reference_day = date(2023, 5, 9)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 1100)
        reference_day = date(2023, 5, 10)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 1200)
        reference_day = date(2023, 5, 20)
        self.assertEqual(contract.compute_amount_to_store_regarding_first_day_of_month(reference_day), 0)
 

class SavingTestCase(TestCase):
    @staticmethod
    def createSampleSaving(
        pk,
        user,
        amount = 100,
        pay_out_day = None
    ):
        return Saving.objects.create(
            pk = pk,
            name = f"saving_{pk}",
            description = f"{pk} saving description",
            user = user,
            amount = amount,
            pay_out_day = pay_out_day
        )
    
    def setUp(self):
        testing_user = User.objects.create(username = "Testing user")
        SavingTestCase.createSampleSaving(1, testing_user)
        SavingTestCase.createSampleSaving(2, testing_user, pay_out_day = date(2022, 5, 10))

    def test_saving(self):
        """Saving is created correctly with the default data"""
        saving = Saving.objects.get(pk=1)
        self.assertEqual(saving.name, "saving_1")
        self.assertEqual(saving.description, "1 saving description")
        self.assertEqual(saving.amount, 100)
        self.assertEqual(saving.user, User.objects.get(username = "Testing user"))
        self.assertEqual(saving.pay_out_day, None)

        saving = Saving.objects.get(pk=2)
        self.assertEqual(saving.pay_out_day, date(2022, 5, 10))

    def test_paid_out(self):
        "Paid out flag is computed correctly based on the reference date"
        saving = Saving.objects.get(pk=1)
        self.assertFalse(saving.paid_out())

        saving = Saving.objects.get(pk=2)
        reference_date = date(2022, 5, 9)
        self.assertFalse(saving.paid_out(reference_date))

        reference_date = date(2022, 5, 10)
        self.assertTrue(saving.paid_out(reference_date))


class RecurringSavingTestCase(TestCase):
    @staticmethod
    def createSampleRecurringSaving(
        pk,
        user,
        start_date = date(2020, 1, 1),
        amount = 100,
        pay_out_day = None,
        end_date = None,
        frequency = Frequency.MONTHLY
    ):
        return RecurringSaving.objects.create(
            pk = pk,
            name = f"recurring_saving_{pk}",
            description = f"{pk} recurring saving description",
            user = user,
            amount = amount,
            pay_out_day = pay_out_day,
            start_date = start_date,
            end_date = end_date,
            frequency = frequency
        )

    def setUp(self):
        testing_user = User.objects.create(username = "Testing user")
        RecurringSavingTestCase.createSampleRecurringSaving(1, testing_user)
        RecurringSavingTestCase.createSampleRecurringSaving(2, testing_user, end_date = date.today() + relativedelta(months=1))
        RecurringSavingTestCase.createSampleRecurringSaving(3, testing_user, end_date = date.today() - relativedelta(months=1))
        RecurringSavingTestCase.createSampleRecurringSaving(
            4,
            testing_user,
            end_date = date.today() - relativedelta(months=2),
            pay_out_day = date.today() - relativedelta(months=2)
        )

    def test_recurring_saving(self):
        """Recurring Saving is created correctly with the default data"""
        saving = RecurringSaving.objects.get(pk=1)
        self.assertEqual(saving.name, "recurring_saving_1")
        self.assertEqual(saving.description, "1 recurring saving description")
        self.assertEqual(saving.amount, 100)
        self.assertEqual(saving.user, User.objects.get(username = "Testing user"))
        self.assertEqual(saving.pay_out_day, None)
        self.assertEqual(saving.start_date, date(2020, 1, 1))
        self.assertEqual(saving.end_date, None)
        self.assertEqual(saving.frequency, Frequency.MONTHLY)

        saving = RecurringSaving.objects.get(pk=2)
        self.assertEqual(saving.end_date, date.today() + relativedelta(months=1))

        saving = RecurringSaving.objects.get(pk=4)
        self.assertEqual(saving.end_date, date.today() - relativedelta(months=2))
        self.assertEqual(saving.pay_out_day, date.today() - relativedelta(months=2))

    def test_paid_out(self):
        "Paid out flag is computed correctly based on the reference date"
        saving = RecurringSaving.objects.get(pk=1)
        self.assertFalse(saving.paid_out())

        saving = RecurringSaving.objects.get(pk=4)
        reference_date = date.today() - relativedelta(months=3)
        self.assertFalse(saving.paid_out(reference_date))

        reference_date = date.today() - relativedelta(months=1)
        self.assertTrue(saving.paid_out(reference_date))


    def test_saved_amount_monthly(self):
        "Saved amount is computed correctly for billing frequency: monthly"
        testing_user = User.objects.create(username = "user_recurring_saving_monthly")
        saving = RecurringSavingTestCase.createSampleRecurringSaving(5, testing_user, start_date=date(2022, 1, 10), amount=150)

        reference_date = date(2022, 5, 9)
        self.assertEqual(saving.saved_amount(reference_date), 600)

        reference_date = date(2022, 5, 10)
        self.assertEqual(saving.saved_amount(reference_date), 750)

    def test_saved_amount_monthly_for_short_months(self):
        "Saved amount is computed correctly for billing frequency: monthly and month shorter than expected billing day"
        testing_user = User.objects.create(username = "user_recurring_saving_monthly_short_months")
        saving = RecurringSavingTestCase.createSampleRecurringSaving(6, testing_user, start_date=date(2022, 1, 31), amount=150)
        reference_date = date(2022, 2, 28)
        self.assertEqual(saving.saved_amount(reference_date), 300)

    def test_saved_amount_monthly_end_date(self):
        "Saved amount is computed correctly for billing frequency: monthly  if end date is set"
        testing_user = User.objects.create(username = "user_recurring_saving_monthly_end_date")
        saving = RecurringSavingTestCase.createSampleRecurringSaving(
            9,
            testing_user,
            start_date=date(2022, 1, 10),
            amount=150,
            end_date=date(2022, 3, 10)
        )

        reference_date = date(2022, 5, 9)
        self.assertEqual(saving.saved_amount(reference_date), 450)

        reference_date = date(2022, 5, 10)
        self.assertEqual(saving.saved_amount(reference_date), 450)

    def test_saved_amount_monthly_pay_out_planned(self):
        "Saved amount is computed correctly for billing frequency: monthly if pay out day in the future"
        testing_user = User.objects.create(username = "user_recurring_saving_monthly_end_date")
        saving = RecurringSavingTestCase.createSampleRecurringSaving(
            9,
            testing_user,
            start_date=date(2022, 1, 10),
            amount=150,
            pay_out_day=date(2022, 10, 10)
        )

        reference_date = date(2022, 5, 9)
        self.assertEqual(saving.saved_amount(reference_date), 600)

        reference_date = date(2022, 5, 10)
        self.assertEqual(saving.saved_amount(reference_date), 750)

    def test_saved_amount_monthly_paid_out(self):
        "Saved amount is computed correctly for billing frequency: monthly if pay out day in the past"
        testing_user = User.objects.create(username = "user_recurring_saving_monthly_end_date")
        saving = RecurringSavingTestCase.createSampleRecurringSaving(
            9,
            testing_user,
            start_date=date(2022, 1, 10),
            amount=150,
            pay_out_day=date(2022, 3, 10)
        )

        reference_date = date(2022, 5, 9)
        self.assertEqual(saving.saved_amount(reference_date), 0)

        reference_date = date(2022, 5, 10)
        self.assertEqual(saving.saved_amount(reference_date), 0)

    def test_saved_amount_quarterly(self):
        "Saved amount is computed correctly for billing frequency: quarterly"
        testing_user = User.objects.create(username = "user_recurring_saving_quarterly")
        saving = RecurringSavingTestCase.createSampleRecurringSaving(
            7,
            testing_user,
            start_date=date(2022, 1, 10),
            amount=150, frequency=Frequency.QUARTERLY
        )

        reference_date = date(2022, 7, 9)
        self.assertEqual(saving.saved_amount(reference_date), 300)

        reference_date = date(2022, 7, 10)
        self.assertEqual(saving.saved_amount(reference_date), 450)

    def test_saved_amount_annually(self):
        "Saved amount is computed correctly for billing frequency: annually"
        testing_user = User.objects.create(username = "user_recurring_saving_annually")
        saving = RecurringSavingTestCase.createSampleRecurringSaving(
            8,
            testing_user,
            start_date=date(2022, 1, 10),
            amount=150, frequency=Frequency.ANNUALY
        )

        reference_date = date(2023, 1, 9)
        self.assertEqual(saving.saved_amount(reference_date), 150)

        reference_date = date(2023, 1, 10)
        self.assertEqual(saving.saved_amount(reference_date), 300)


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username = "NoFirstDay")
        User.objects.create(username = "FirstDay1", first_day_of_the_month = 1)
        User.objects.create(username = "FirstDay10", first_day_of_the_month = 10)
        User.objects.create(username = "FirstDay31", first_day_of_the_month = 31)

    def test_beginning_of_current_month(self):
        "Beginning of the current month is computed correctly"
        reference_date = date(2023, 3, 9)
        self.assertEqual(User.objects.get(username = "NoFirstDay").beginning_of_current_month(reference_date), date(2023, 3, 1))
        self.assertEqual(User.objects.get(username = "FirstDay1").beginning_of_current_month(reference_date), date(2023, 3, 1))
        self.assertEqual(User.objects.get(username = "FirstDay10").beginning_of_current_month(reference_date), date(2023, 2, 10))
        self.assertEqual(User.objects.get(username = "FirstDay31").beginning_of_current_month(reference_date), date(2023, 2, 28))

    def test_beginning_of_next_month(self):
        "Beginning of the next month is computed correctly"
        reference_date = date(2023, 3, 9)
        self.assertEqual(User.objects.get(username = "NoFirstDay").beginning_of_next_month(reference_date), date(2023, 4, 1))
        self.assertEqual(User.objects.get(username = "FirstDay1").beginning_of_next_month(reference_date), date(2023, 4, 1))
        self.assertEqual(User.objects.get(username = "FirstDay10").beginning_of_next_month(reference_date), date(2023, 3, 10))
        self.assertEqual(User.objects.get(username = "FirstDay31").beginning_of_next_month(reference_date), date(2023, 3, 31))

    def test_create_statistics_one_contract_monthly(self):
        "Statistics are computed correctly for user with one contract with billing frequency: monthly"
        user =  User.objects.create(username = "StatisticsContractMonthly", first_day_of_the_month = 5)
        ContractTestCase.createSampleContract(101, user, first_billing_day = date(2022, 5, 20), amount=200)

        reference_date = date(2022, 10, 1)
        expected_statistics = Statistics(
            balance=10000,
            savings=[],
            active_contracts=[
                StatisticContract("contract_101", date(2022, 10, 20), 200, 0)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 10, 10)
        expected_statistics = Statistics(
            balance=9800,
            savings=[],
            active_contracts=[
                StatisticContract("contract_101", date(2022, 10, 20), 200, 200)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

    def test_create_statistics_one_contract_quarterly(self):
        "Statistics are computed correctly for user with one contract with billing frequency: quarterly"
        user =  User.objects.create(username = "StatisticsContractMonthly", first_day_of_the_month = 5)
        ContractTestCase.createSampleContract(
            102,
            user,
            first_billing_day = date(2022, 5, 20),
            amount=2100,
            frequency=Frequency.QUARTERLY
        )

        reference_date = date(2022, 8, 21)
        expected_statistics = Statistics(
            balance=10000,
            savings=[],
            active_contracts=[
                StatisticContract("contract_102", date(2022, 11, 20), 2100, 0)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 9, 4)
        expected_statistics = Statistics(
            balance=10000,
            savings=[],
            active_contracts=[
                StatisticContract("contract_102", date(2022, 11, 20), 2100, 0)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 9, 5)
        expected_statistics = Statistics(
            balance=9300,
            savings=[],
            active_contracts=[
                StatisticContract("contract_102", date(2022, 11, 20), 2100, 700)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 10, 4)
        expected_statistics = Statistics(
            balance=9300,
            savings=[],
            active_contracts=[
                StatisticContract("contract_102", date(2022, 11, 20), 2100, 700)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 10, 5)
        expected_statistics = Statistics(
            balance=8600,
            savings=[],
            active_contracts=[
                StatisticContract("contract_102", date(2022, 11, 20), 2100, 1400)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 11, 5)
        expected_statistics = Statistics(
            balance=7900,
            savings=[],
            active_contracts=[
                StatisticContract("contract_102", date(2022, 11, 20), 2100, 2100)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 11, 19)
        expected_statistics = Statistics(
            balance=7900,
            savings=[],
            active_contracts=[
                StatisticContract("contract_102", date(2022, 11, 20), 2100, 2100)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

    def test_create_statistics_one_contract_annually(self):
        "Statistics are computed correctly for user with one contract with billing frequency: annually"
        user =  User.objects.create(username = "StatisticsContractMonthly", first_day_of_the_month = 5)
        ContractTestCase.createSampleContract(
            103,
            user,
            first_billing_day = date(2022, 5, 20),
            amount=1200,
            frequency=Frequency.ANNUALY
        )

        reference_date = date(2022, 5, 21)
        expected_statistics = Statistics(
            balance=10000,
            savings=[],
            active_contracts=[
                StatisticContract("contract_103", date(2023, 5, 20), 1200, 0)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)


        reference_date = date(2022, 8, 21)
        expected_statistics = Statistics(
            balance=9700,
            savings=[],
            active_contracts=[
                StatisticContract("contract_103", date(2023, 5, 20), 1200, 300)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2022, 9, 5)
        expected_statistics = Statistics(
            balance=9600,
            savings=[],
            active_contracts=[
                StatisticContract("contract_103", date(2023, 5, 20), 1200, 400)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2023, 5, 4)
        expected_statistics = Statistics(
            balance=8900,
            savings=[],
            active_contracts=[
                StatisticContract("contract_103", date(2023, 5, 20), 1200, 1100)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)

        reference_date = date(2023, 5, 5)
        expected_statistics = Statistics(
            balance=8800,
            savings=[],
            active_contracts=[
                StatisticContract("contract_103", date(2023, 5, 20), 1200, 1200)
            ]
        )
        self.assertEqual(user.create_statistics(10000, reference_date), expected_statistics)


    def test_create_statistics_multiple_contracts(self):
        "Statistics are computed correctly for user with multiple contracts"
        user =  User.objects.create(username = "StatisticsManyContacts", first_day_of_the_month = 5)
        ContractTestCase.createSampleContract(
            104,
            user,
            first_billing_day = date(2022, 5, 20),
            amount=2100,
            frequency=Frequency.QUARTERLY
        )
        ContractTestCase.createSampleContract(
            105,
            user,
            first_billing_day = date(2022, 5, 10),
            amount=2100,
            frequency=Frequency.MONTHLY
        )

        reference_date = date(2022, 5, 20)
        active_contracts=[
                StatisticContract("contract_104", date(2022, 8, 20), 2100, 0),
                StatisticContract("contract_105", date(2022, 6, 10), 2100, 0)
            ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 10000)
        self.assertCountEqual(statistics.active_contracts, active_contracts)

        reference_date = date(2022, 6, 5)
        active_contracts=[
                StatisticContract("contract_104", date(2022, 8, 20), 2100, 700),
                StatisticContract("contract_105", date(2022, 6, 10), 2100, 2100)
            ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 7200)
        self.assertCountEqual(statistics.active_contracts, active_contracts)

        reference_date = date(2022, 6, 10)
        active_contracts=[
                StatisticContract("contract_104", date(2022, 8, 20), 2100, 700),
                StatisticContract("contract_105", date(2022, 7, 10), 2100, 0)
            ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 9300)
        self.assertCountEqual(statistics.active_contracts, active_contracts)

        reference_date = date(2022, 8, 8)
        active_contracts=[
                StatisticContract("contract_104", date(2022, 8, 20), 2100, 2100),
                StatisticContract("contract_105", date(2022, 8, 10), 2100, 2100)
            ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 5800)
        self.assertCountEqual(statistics.active_contracts, active_contracts)


        reference_date = date(2022, 8, 10)
        active_contracts=[
                StatisticContract("contract_104", date(2022, 8, 20), 2100, 2100),
                StatisticContract("contract_105", date(2022, 9, 10), 2100, 0)
            ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 7900)
        self.assertCountEqual(statistics.active_contracts, active_contracts)

        
    def test_create_statistics_multiple_savings(self):
        "Statistics are computed correctly for user with multiple savings"
        user =  User.objects.create(username = "ManySavings", first_day_of_the_month = 5)
        SavingTestCase.createSampleSaving(106, user, amount=2000)
        SavingTestCase.createSampleSaving(107, user, amount=2000)
        SavingTestCase.createSampleSaving(108, user, amount=2000, pay_out_day=date(2022, 5, 10))

        reference_date = date(2022, 5, 9)
        savings = [
            StatisticSaving("saving_106", False, 2000),
            StatisticSaving("saving_107", False, 2000),
            StatisticSaving("saving_108", False, 2000)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 4000)
        self.assertCountEqual(statistics.savings, savings)

        reference_date = date(2022, 5, 10)
        savings = [
            StatisticSaving("saving_106", False, 2000),
            StatisticSaving("saving_107", False, 2000)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 6000)
        self.assertCountEqual(statistics.savings, savings)

    def test_create_statistics_one_recurring_saving_monthly(self):
        "Statistics are computed correctly for user with one recurring saving with frequency: monthly"
        user =  User.objects.create(username = "ManyRecurringSavings", first_day_of_the_month = 5)
        RecurringSavingTestCase.createSampleRecurringSaving(109, user, start_date = date(2022, 5, 20), amount = 100)

        reference_date = date(2022, 5, 20)
        savings = [
            StatisticSaving("recurring_saving_109", True, 100)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 9900)
        self.assertCountEqual(statistics.savings, savings)

        reference_date = date(2023, 2, 20)
        savings = [
            StatisticSaving("recurring_saving_109", True, 1000)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 9000)
        self.assertCountEqual(statistics.savings, savings)


    def test_create_statistics_one_recurring_saving_quarterly(self):
        "Statistics are computed correctly for user with one recurring saving with frequency: quarterly"
        user =  User.objects.create(username = "RecurringSavingsQuarterly", first_day_of_the_month = 5)
        RecurringSavingTestCase.createSampleRecurringSaving(
            110,
            user,
            start_date = date(2022, 5, 20),
            amount = 100,
            frequency=Frequency.QUARTERLY
        )

        reference_date = date(2022, 5, 20)
        savings = [
            StatisticSaving("recurring_saving_110", True, 100)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 9900)
        self.assertCountEqual(statistics.savings, savings)

        reference_date = date(2022, 9, 20)
        savings = [
            StatisticSaving("recurring_saving_110", True, 200)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 9800)
        self.assertCountEqual(statistics.savings, savings)

    def test_create_statistics_one_recurring_saving_annually(self):
        "Statistics are computed correctly for user with one recurring saving with frequency: annually"
        user =  User.objects.create(username = "RecurringSavingsQuarterly", first_day_of_the_month = 5)
        RecurringSavingTestCase.createSampleRecurringSaving(
            111,
            user,
            start_date = date(2022, 5, 20),
            amount = 100,
            frequency=Frequency.ANNUALY
        )

        reference_date = date(2022, 5, 20)
        savings = [
            StatisticSaving("recurring_saving_111", True, 100)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 9900)
        self.assertCountEqual(statistics.savings, savings)

        reference_date = date(2023, 5, 20)
        savings = [
            StatisticSaving("recurring_saving_111", True, 200)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 9800)
        self.assertCountEqual(statistics.savings, savings)

    def test_create_statistics_multiple_recurring_savings(self):
        "Statistics are computed correctly for user with multiple recurring savings"
        user =  User.objects.create(username = "RecurringSavingsQuarterly", first_day_of_the_month = 5)
        RecurringSavingTestCase.createSampleRecurringSaving(
            112,
            user,
            start_date = date(2022, 5, 20),
            amount = 100,
            frequency=Frequency.MONTHLY
        )
        RecurringSavingTestCase.createSampleRecurringSaving(
            113,
            user,
            start_date = date(2022, 2, 20),
            amount = 100,
            frequency=Frequency.ANNUALY
        )
        reference_date = date(2023, 5, 20)
        savings = [
            StatisticSaving("recurring_saving_112", True, 1300),
            StatisticSaving("recurring_saving_113", True, 200)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 8500)
        self.assertCountEqual(statistics.savings, savings)

    def test_create_statistics_multiple_contracts_and_savings(self):
        "Statistics are computed correctly for user with multiple contracts and savings"
        user =  User.objects.create(username = "RecurringSavingsQuarterly", first_day_of_the_month = 5)
        RecurringSavingTestCase.createSampleRecurringSaving(
            114,
            user,
            start_date = date(2022, 5, 20),
            amount = 100,
            frequency=Frequency.MONTHLY
        )
        SavingTestCase.createSampleSaving(115, user, amount=2000)
        SavingTestCase.createSampleSaving(116, user, amount=2000, pay_out_day=date(2022, 8, 10))
        ContractTestCase.createSampleContract(
            117,
            user,
            first_billing_day = date(2022, 5, 10),
            amount=2100,
            frequency=Frequency.MONTHLY
        )

        reference_date = date(2022, 7, 30)
        active_contracts=[
                StatisticContract("contract_117", date(2022, 8, 10), 2100, 0),
        ]
        savings = [
            StatisticSaving("saving_115", False, 2000),
            StatisticSaving("saving_116", False, 2000),
            StatisticSaving("recurring_saving_114", True, 300)
        ]
        statistics = user.create_statistics(10000, reference_date)
        self.assertEqual(statistics.balance, 5700)
        self.assertCountEqual(statistics.savings, savings)
        self.assertCountEqual(statistics.active_contracts, active_contracts)