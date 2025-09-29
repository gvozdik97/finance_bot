# keyboards/transactions_menu.py
from telegram import ReplyKeyboardMarkup

def get_transactions_menu_keyboard():
    """Клавиатура меню управления транзакциями"""
    keyboard = [
        ['💳 Добавить доход', '💸 Добавить расход'],
        ['📋 История операций', '✏️ Редактировать'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)