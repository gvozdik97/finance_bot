# finance_bot/database/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    id: Optional[int] = None
    user_id: Optional[int] = None
    type: Optional[str] = None  # 'income' or 'expense'
    amount: float = 0.0
    category: str = ""
    description: str = ""
    date: Optional[datetime] = None

@dataclass
class Budget:
    id: Optional[int] = None
    user_id: Optional[int] = None
    category: str = ""
    amount: float = 0.0
    period: str = "monthly"  # 'monthly' or 'weekly'
    created_at: Optional[datetime] = None

# === НОВЫЕ МОДЕЛИ ДЛЯ ВАВИЛОНСКОЙ СИСТЕМЫ ===

@dataclass
class Wallet:
    """Модель виртуальных кошельков по правилам Вавилона"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    wallet_type: str = ""  # 'gold_reserve' | 'living_budget' | 'debt_repayment'
    balance: float = 0.0
    created_at: Optional[datetime] = None

@dataclass
class BabylonRuleProgress:
    """Отслеживание прогресса по правилам книги"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    rule_name: str = ""  # '10_percent_rule', 'control_expenses', 'debt_free', 'wise_investment'
    is_active: bool = True
    progress: float = 0.0  # 0-100%
    last_updated: Optional[datetime] = None

@dataclass
class Debt:
    """Модель для учета долгов (будет использоваться в Фазе 2)"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    creditor: str = ""  # Кому должны
    initial_amount: float = 0.0
    current_amount: float = 0.0
    interest_rate: float = 0.0  # Процентная ставка
    due_date: Optional[datetime] = None
    status: str = "active"  # 'active', 'paid', 'overdue'
    created_at: Optional[datetime] = None