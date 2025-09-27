# services/__init__.py

from .wallet_service import wallet_service
from .babylon_service import babylon_service
from .transaction_service import transaction_service
from .debt_service import debt_service
from .financial_analytics import financial_analytics  # ← НОВЫЙ ИМПОРТ

# Удаляем старые сложные сервисы
# from .advanced_analytics import advanced_analytics  # ← КОММЕНТИРУЕМ
# from .trend_analyzer import trend_analyzer  # ← КОММЕНТИРУЕМ

__all__ = [
    'wallet_service',
    'babylon_service', 
    'transaction_service',
    'debt_service',
    'financial_analytics',  # ← НОВЫЙ
]