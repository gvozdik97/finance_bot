# finance_bot/keyboards/budgets_menu.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.constants import EXPENSE_CATEGORIES

def get_budgets_main_keyboard():
    """Возвращает основную клавиатуру управления бюджетами"""
    keyboard = [
        [InlineKeyboardButton("📊 Мои бюджеты", callback_data="budget_list")],
        [InlineKeyboardButton("➕ Добавить бюджет", callback_data="budget_add")],
        [InlineKeyboardButton("✏️ Изменить бюджет", callback_data="budget_edit")],
        [InlineKeyboardButton("❌ Удалить бюджет", callback_data="budget_delete")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_budget_categories_keyboard():
    """Возвращает клавиатуру выбора категории для бюджета"""
    from utils.categorizers import clean_category_name
    
    keyboard = []
    for i in range(0, len(EXPENSE_CATEGORIES), 2):
        row = []
        for j in range(2):
            if i + j < len(EXPENSE_CATEGORIES):
                cat = EXPENSE_CATEGORIES[i + j]
                clean_cat = clean_category_name(cat)
                row.append(InlineKeyboardButton(cat, callback_data=f"budget_cat_{clean_cat}"))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

def get_user_budgets_keyboard(user_budgets, action_prefix: str):
    """Возвращает клавиатуру с бюджетами пользователя для действий (изменение/удаление)"""
    keyboard = []
    for category, amount in user_budgets:
        keyboard.append([
            InlineKeyboardButton(
                f"{category} ({amount} руб.)", 
                callback_data=f"{action_prefix}_{category}"
            )
        ])
    
    # Добавляем кнопку отмены
    cancel_text = "cancel_edit" if action_prefix == "edit_budget" else "cancel_delete"
    cancel_button = InlineKeyboardButton("❌ Отмена", callback_data=cancel_text)
    keyboard.append([cancel_button])
    
    return InlineKeyboardMarkup(keyboard)

def get_overwrite_budget_keyboard(amount: float):
    """Возвращает клавиатуру для подтверждения перезаписи бюджета"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Перезаписать", callback_data=f"overwrite_budget_{amount}"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_overwrite")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)