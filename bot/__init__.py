# bot/__init__.py - ЧИСТАЯ ВАВИЛОНСКАЯ АРХИТЕКТУРА

"""
Вавилонский финансовый бот - чистый модуль обработчиков
Только правила 10%/90%, никакой старой логики
"""

from .common import show_main_menu, show_main_menu_from_query

# Основные обработчики
from .handlers import (
    start,
    show_wallets,
    show_simple_stats,
    show_babylon_rules,
    show_help,
    handle_menu_commands
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

# Упрощенный список экспортируемых функций
__all__ = [
    # Common functions
    'show_main_menu',
    'show_main_menu_from_query',
    
    # Main handlers
    'start',
    'show_wallets', 
    'show_simple_stats',
    'show_babylon_rules',
    'show_help',
    'handle_menu_commands',
    
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

# Убрали все старые импорты:
# - reports_handlers (удалили)
# - budgets_handlers (удалили) 
# - сложные обработчики бюджетов (упростили)