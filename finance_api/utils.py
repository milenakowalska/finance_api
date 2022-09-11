from datetime import date
from .models import Contract, Saving, RecurringSaving
from dataclasses import dataclass
import calendar

@dataclass
class Statistics:
    balance: float
    savings: list
    remaining_contracts: list

    def __init__(self, balance, savings, remaining_contracts):
        self.balance = balance
        self.savings = savings
        self.remaining_contracts = remaining_contracts

    def show(self):
        savings = []
        for saving in self.savings:
            new_saving = {"name": saving.name, "recurring": saving.recurring, "total_saved": saving.total_saved}
            savings.append(new_saving)

        contracts = []
        for contract in self.remaining_contracts:
            new_contract = {"name": contract.name, "billing_date": contract.billing_date, "amount": contract.amount}
            contracts.append(new_contract)

        statistics_dict = {"disponible": self.balance, "savings": savings, "remaining_contracts": contracts}
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

    def __init__(self, name, billing_date, amount):
        self.name = name
        self.billing_date = billing_date
        self.amount = amount


def create_statistics(user, balance, reference_date):
    all_savings = []
    remaining_contracts = []
    user_contracts = Contract.objects.all().filter(user = user)
    user_savings = Saving.objects.all().filter(user = user)
    user_recurring_savings = RecurringSaving.objects.all().filter(user = user)

    for saving in user_savings:
        all_savings.append(StatisticSaving(saving.name, False, saving.amount))
        balance -= saving.amount

    for recurring_saving in user_recurring_savings:
        total_saved = recurring_saving.saved_amount(reference_date)
        all_savings.append(StatisticSaving(recurring_saving.name, True, total_saved))
        balance -= recurring_saving.amount

    for contract in user_contracts:
        try: 
            contract_date = contract.first_billing_day
            billing_day = date(reference_date.year, reference_date.month, contract_date.day)
        except ValueError:
            last_day = calendar.monthrange(reference_date.year, reference_date.month)[1]
            billing_day = date(reference_date.year, reference_date.month, last_day)

        if billing_day < reference_date:
            amount = 0 if contract.amount is None else contract.amount
            remaining_contracts.append(StatisticContract(contract.name, billing_day, amount))
            balance -= amount

    return Statistics(balance, all_savings, remaining_contracts)