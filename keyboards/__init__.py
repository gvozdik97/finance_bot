# keyboards/__init__.py - УПРОЩАЕМ

from .main_menu import get_main_menu_keyboard, get_category_keyboard, remove_keyboard

__all__ = [
    'get_main_menu_keyboard',
    'get_category_keyboard', 
    'remove_keyboard'
    # Убрали сложные меню отчетов и бюджетов
]