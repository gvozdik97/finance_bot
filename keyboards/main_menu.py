# finance_bot/keyboards/main_menu.py

from telegram import ReplyKeyboardMarkup

def get_main_menu_keyboard():
    """Возвращает клавиатуру главного меню"""
    keyboard = [
        ['💸 Добавить расход', '💳 Добавить доход'],
        ['📊 Отчеты и аналитика', '💰 Бюджеты'],
        ['📈 Статистика', '📤 Экспорт данных'],
        ['ℹ️ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_category_keyboard(transaction_type: str):
    """Возвращает клавиатуру с категориями для расходов/доходов"""
    from utils.constants import EXPENSE_CATEGORIES, INCOME_CATEGORIES
    
    categories = EXPENSE_CATEGORIES if transaction_type == 'expense' else INCOME_CATEGORIES
    keyboard = [[cat] for cat in categories]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def remove_keyboard():
    """Возвращает объект для удаления клавиатуры"""
    from telegram import ReplyKeyboardRemove
    return ReplyKeyboardRemove()