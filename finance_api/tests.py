from datetime import date
from django.test import TestCase
from .models import Contract
from django.contrib.auth.models import User

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
        self.assertEqual(internet_contract.billing_frequency, Contract.Frequency.MONTHLY)
