# finance_bot/keyboards/reports_menu.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_reports_keyboard():
    """Возвращает инлайн-клавиатуру для выбора периода отчетов"""
    keyboard = [
        [
            InlineKeyboardButton("📅 Неделя", callback_data="report_7"),
            InlineKeyboardButton("📅 Месяц", callback_data="report_30")
        ],
        [
            InlineKeyboardButton("📅 Квартал", callback_data="report_90"),
            InlineKeyboardButton("📅 Год", callback_data="report_365")
        ],
        [
            InlineKeyboardButton("📊 Текущий месяц", callback_data="report_current"),
            InlineKeyboardButton("📊 Прошлый месяц", callback_data="report_previous")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)