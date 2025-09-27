# services/__init__.py - ОБНОВЛЯЕМ ДЛЯ ФАЗЫ 2

from .wallet_service import wallet_service
from .babylon_service import babylon_service
from .transaction_service import transaction_service
from .simple_budget_service import simple_budget_service
from .debt_service import debt_service  # ✅ ДОБАВИЛИ ДЛЯ ФАЗЫ 2

__all__ = [
    'wallet_service',
    'babylon_service', 
    'transaction_service',
    'simple_budget_service',
    'debt_service'  # ✅ ДОБАВИЛИ
]