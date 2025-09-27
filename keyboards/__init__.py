# keyboards/__init__.py

from .main_menu import get_main_menu_keyboard, get_category_keyboard, remove_keyboard, get_debt_management_keyboard
from .analytics_menu import get_analytics_menu_keyboard

__all__ = [
    'get_main_menu_keyboard',
    'get_category_keyboard', 
    'remove_keyboard',
    'get_debt_management_keyboard',
    'get_analytics_menu_keyboard',
]