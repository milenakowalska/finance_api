from datetime import date
from .models import Contract, Saving, RecurringSaving
from dataclasses import dataclass


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

