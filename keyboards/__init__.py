# keyboards/__init__.py - ФИНАЛЬНАЯ ВЕРСИЯ
from .main_menu import get_main_menu_keyboard, get_category_keyboard, remove_keyboard, get_debt_management_keyboard
from .analytics_menu import get_analytics_menu_keyboard
from .debt_menu import get_debt_management_keyboard as get_debt_menu_keyboard
from .transactions_menu import get_transactions_menu_keyboard
from .budget_menu import get_budget_management_keyboard, get_budget_categories_keyboard, get_budget_confirmation_keyboard
from .settings_menu import get_settings_menu_keyboard, get_savings_options_keyboard, get_edit_transactions_keyboard, get_edit_confirmation_keyboard

__all__ = [
    'get_main_menu_keyboard',
    'get_category_keyboard', 
    'remove_keyboard',
    'get_debt_management_keyboard',
    'get_analytics_menu_keyboard',
    'get_debt_menu_keyboard',
    'get_transactions_menu_keyboard',
    'get_budget_management_keyboard',
    'get_budget_categories_keyboard',
    'get_budget_confirmation_keyboard',
    'get_settings_menu_keyboard',
    'get_savings_options_keyboard',
    'get_edit_transactions_keyboard',
    'get_edit_confirmation_keyboard',
]