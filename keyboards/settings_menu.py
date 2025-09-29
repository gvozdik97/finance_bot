# keyboards/settings_menu.py
from telegram import ReplyKeyboardMarkup

def get_settings_menu_keyboard():
    """Клавиатура меню настроек"""
    keyboard = [
        ['⚙️ Настройки накоплений', '📊 Текущие настройки'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_savings_options_keyboard():
    """Клавиатура выбора стратегии накоплений"""
    keyboard = [
        ['💰 Классические 10%', '💸 Без накоплений'],
        ['🎯 Настроить процент', '🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_edit_transactions_keyboard():
    """Клавиатура меню редактирования транзакций"""
    keyboard = [
        ['✏️ Выбрать транзакцию', '🗑️ Удалить транзакцию'],
        ['📋 Список транзакций', '🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_edit_confirmation_keyboard():
    """Клавиатура подтверждения редактирования"""
    keyboard = [
        ['✅ Подтвердить', '❌ Отменить'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)