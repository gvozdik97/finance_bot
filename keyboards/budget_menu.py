# keyboards/budget_menu.py
from telegram import ReplyKeyboardMarkup

def get_budget_management_keyboard():
    """Упрощенная клавиатура меню управления бюджетами"""
    keyboard = [
        ['💰 Мои бюджеты', '🎯 Установить бюджет'],
        ['💡 Рекомендации', '🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_budget_categories_keyboard():
    """Клавиатура выбора категорий для бюджета"""
    from utils.constants import EXPENSE_CATEGORIES
    # Убираем эмодзи для чистых названий категорий
    categories = [cat.replace('🍎', '').replace('🚗', '').replace('🎮', '').replace('🏠', '')
                 .replace('👕', '').replace('🏥', '').replace('📚', '').replace('📦', '').strip() 
                 for cat in EXPENSE_CATEGORIES]
    
    keyboard = []
    for i in range(0, len(categories), 2):
        if i + 1 < len(categories):
            keyboard.append([categories[i], categories[i + 1]])
        else:
            keyboard.append([categories[i]])
    
    keyboard.append(['🏠 Главное меню'])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_budget_confirmation_keyboard():
    """Клавиатура подтверждения перезаписи бюджета"""
    keyboard = [
        ['✅ Да, перезаписать', '❌ Нет, отменить'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)