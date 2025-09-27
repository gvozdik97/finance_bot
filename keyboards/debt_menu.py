# keyboards/debt_menu.py - РАБОЧАЯ ВЕРСИЯ

from telegram import ReplyKeyboardMarkup

def get_debt_management_keyboard():
    """Клавиатура для раздела управления долгами"""
    keyboard = [
        ['📜 Мои долги', '💳 Погасить долг'],
        ['➕ Добавить долг', '📋 План погашения'],
        ['📈 Прогресс свободы', '🎯 Вехи освобождения'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_debt_selection_keyboard(debts):
    """Клавиатура для выбора конкретного долга"""
    keyboard = []
    for i, debt in enumerate(debts, 1):
        keyboard.append([f"{i}. {debt.creditor} - {debt.current_amount:,.0f} руб."])
    
    keyboard.append(['🔙 Назад к долгам'])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)