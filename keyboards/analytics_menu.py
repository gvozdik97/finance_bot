# keyboards/analytics_menu.py

from telegram import ReplyKeyboardMarkup

def get_advanced_analytics_menu_keyboard():
    """Меню расширенной аналитики с новыми возможностями"""
    keyboard = [
        ['🏛️ Финансовое здоровье', '🔮 Прогноз накоплений'],
        ['📊 Анализ расходов', '📈 Тренды доходов'],
        ['🎯 Паттерны расходов', '🎨 Визуализации'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_visualizations_menu_keyboard():
    """Меню визуализаций в вавилонском стиле"""
    keyboard = [
        ['🏔️ Пирамида стабильности', '🏛️ Храм богатства'],
        ['🌊 Реки удачи', '✨ Финансовый гороскоп'],
        ['📜 Месячная летопись', '🔙 Назад к аналитике'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)