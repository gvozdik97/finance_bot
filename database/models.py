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