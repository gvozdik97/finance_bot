# keyboards/main_menu.py - ОБНОВЛЕННАЯ ВЕРСИЯ С АНАЛИТИКОЙ

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

def get_main_menu_keyboard():
    """Главное меню с кнопкой аналитики"""
    keyboard = [
        ['💳 Добавить доход', '💸 Добавить расход'],
        ['🏦 Мои кошельки', '📊 Простая статистика'],
        ['📈 Финансовая аналитика', '🏛️ Правила Вавилона'],  # ✅ ДОБАВИЛИ АНАЛИТИКУ
        ['📜 Долги', 'ℹ️ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_analytics_menu_keyboard():
    """Меню расширенной аналитики"""
    keyboard = [
        ['🏛️ Финансовое здоровье', '🔮 Прогноз накоплений'],
        ['📊 Анализ расходов', '🎯 Персональные рекомендации'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_debt_management_keyboard():
    """Меню управления долгами"""
    keyboard = [
        ['📜 Мои долги', '💳 Погасить долг'],
        ['➕ Добавить долг', '📋 План погашения'],
        ['📈 Прогресс свободы', '🎯 Вехи освобождения'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_category_keyboard(transaction_type: str):
    """Простой выбор категорий"""
    from utils.constants import EXPENSE_CATEGORIES, INCOME_CATEGORIES
    
    categories = EXPENSE_CATEGORIES if transaction_type == 'expense' else INCOME_CATEGORIES
    keyboard = [[cat] for cat in categories]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def remove_keyboard():
    """Убирает клавиатуру"""
    return ReplyKeyboardRemove()