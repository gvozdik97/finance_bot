# bot/__init__.py - ОБНОВЛЕННЫЕ ИМПОРТЫ

"""
Вавилонский финансовый бот - оптимизированная версия
"""

from .common import show_main_menu, show_main_menu_from_query

# Основные обработчики
from .handlers import (
    start,
    show_wallets,
    show_babylon_rules,
    show_help,
    handle_menu_commands,
    show_debts_main_menu
)

# Обработчики аналитики
from .analytics_handlers import (
    show_analytics_menu,
    handle_analytics_commands,
    show_financial_overview,
    show_spending_analysis,
    show_income_analysis,
    show_financial_charts
)

# Обработчики транзакций и диалогов
from .conversations import (
    add_income,
    add_expense,
    amount_handler,
    category_handler,
    save_transaction,
    quick_input,
    create_transaction_conversation_handler
)

# Убираем старые сложные импорты аналитики

__all__ = [
    # Common functions
    'show_main_menu',
    'show_main_menu_from_query',
    
    # Main handlers
    'start',
    'show_wallets', 
    'show_babylon_rules',
    'show_help',
    'handle_menu_commands',
    'show_debts_main_menu',
    
    # Analytics handlers
    'show_analytics_menu',
    'handle_analytics_commands',
    'show_financial_overview',
    'show_spending_analysis',
    'show_income_analysis',
    'show_financial_charts',
    
    # Transaction handlers
    'add_income',
    'add_expense',
    'amount_handler',
    'category_handler',
    'save_transaction',
    'quick_input',
    
    # Conversation handlers
    'create_transaction_conversation_handler'
]