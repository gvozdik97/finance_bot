# keyboards/analytics_menu.py - УПРОЩЕННОЕ МЕНЮ АНАЛИТИКИ

from telegram import ReplyKeyboardMarkup

def get_analytics_menu_keyboard():
    """Упрощенное меню аналитики с понятными опциями"""
    keyboard = [
        ['📊 Финансовый обзор', '📈 Анализ расходов'],
        ['💰 Динамика доходов', '📉 Графики и отчеты'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)