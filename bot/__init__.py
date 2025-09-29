# bot/__init__.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
Вавилонский финансовый бот - полная версия с новым функционалом
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

# Обработчики транзакций
from .transactions_handlers import (
    show_transactions_menu,
    show_transaction_history,
    handle_transactions_menu_commands
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

# Обработчики бюджетирования
from .budget_handlers import (
    show_budgets_menu,
    show_my_budgets,
    show_budget_recommendations,
    handle_budget_menu_commands,
    create_budget_conversation_handler
)

# Обработчики настроек
from .settings_handlers import (
    show_settings_menu,
    show_current_settings,
    handle_settings_menu_commands,
    create_settings_conversation_handler
)

# Обработчики редактирования транзакций
from .transaction_editor_handlers import (
    show_edit_menu,
    handle_edit_menu_commands,
    create_edit_conversation_handler
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

# Обработчики долгов - ИСПРАВЛЕННЫЕ ИМПОРТЫ
from .debt_handlers import (
    show_debts_menu,
    show_snowball_plan,
    show_debt_freedom_progress,
    show_debt_milestones
)

from .debt_conversations import create_debt_conversation_handler
from .debt_menu_handlers import handle_debt_menu_commands  # ← ПРАВИЛЬНЫЙ ИМПОРТ

# Conversation handlers для долгов
from .debt_handlers import create_debt_payment_conversation_handler

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
    
    # Transactions handlers
    'show_transactions_menu',
    'show_transaction_history',
    'handle_transactions_menu_commands',
    
    # Analytics handlers
    'show_analytics_menu',
    'handle_analytics_commands',
    'show_financial_overview',
    'show_spending_analysis',
    'show_income_analysis',
    'show_financial_charts',
    
    # Budget handlers
    'show_budgets_menu',
    'show_my_budgets',
    'show_budget_recommendations',
    'handle_budget_menu_commands',
    'create_budget_conversation_handler',
    
    # Settings handlers
    'show_settings_menu',
    'show_current_settings',
    'handle_settings_menu_commands',
    'create_settings_conversation_handler',
    
    # Transaction editor handlers
    'show_edit_menu',
    'handle_edit_menu_commands',
    'create_edit_conversation_handler',
    
    # Transaction handlers
    'add_income',
    'add_expense',
    'amount_handler',
    'category_handler',
    'save_transaction',
    'quick_input',
    
    # Conversation handlers
    'create_transaction_conversation_handler',
    'create_debt_conversation_handler',
    'create_debt_payment_conversation_handler',
    
    # Debt handlers
    'show_debts_menu',
    'show_snowball_plan',
    'show_debt_freedom_progress',
    'show_debt_milestones',
    'handle_debt_menu_commands'  # ← ДОБАВЛЯЕМ СЮДА
]