from datetime import date
from distutils import archive_util
from .models import Contract, Saving, RecurringSaving
from dataclasses import dataclass
import calendar

@dataclass
class Statistics:
    balance: float
    savings: list
    active_contracts: list

    def __init__(self, balance, savings, active_contracts):
        self.balance = balance
        self.savings = savings
        self.active_contracts = active_contracts

    def show(self):
        savings = []
        for saving in self.savings:
            new_saving = {"name": saving.name, "recurring": saving.recurring, "total_saved": saving.total_saved}
            savings.append(new_saving)

        contracts = []
        for contract in self.active_contracts:
            new_contract = {
                "name": contract.name,
                "billing_date": contract.billing_date,
                "amount": contract.amount,
                "stored_until_next_billing": contract.stored
                }
            contracts.append(new_contract)

        statistics_dict = {"disponible": self.balance, "savings": savings, "active_contracts": contracts}
        return statistics_dict


@dataclass
class StatisticSaving:
    name: str
    recurring: bool
    total_saved: float

    def __init__(self, name, recurring, total_saved):
        self.name = name
        self.recurring = recurring
        self.total_saved = total_saved


@dataclass
class StatisticContract:
    name: str
    billing_date: date
    amount: float

    def __init__(self, name, billing_date, amount, stored):
        self.name = name
        self.billing_date = billing_date
        self.amount = amount
        self.stored = stored


def create_statistics(user, balance, reference_date):
    all_savings = []
    active_contracts = []
    user_contracts = Contract.objects.all().filter(user = user)
    user_savings = Saving.objects.all().filter(user = user)
    user_recurring_savings = RecurringSaving.objects.all().filter(user = user)

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
            to_store = contract.compute_amount_to_store(reference_date)

            active_contracts.append(StatisticContract(contract.name, billing_day, contract.amount, to_store))
            balance -= to_store

    return Statistics(balance, all_savings, active_contracts)
