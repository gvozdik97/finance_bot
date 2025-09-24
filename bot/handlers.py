# finance_bot/bot/handlers.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.constants import AMOUNT
from keyboards.main_menu import get_main_menu_keyboard, remove_keyboard
from services.budget_service import budget_service
from services.export_service import export_service
from services.analytics_service import analytics_service

from .common import show_main_menu, show_main_menu_from_query

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.message.from_user
    welcome_text = f"""
💰 *Финансовый помощник*

Привет, {user.first_name}! Выберите действие:

*💸 Добавить расход* - Внести трату
*💳 Добавить доход* - Внести доход  
*📊 Отчеты* - Графики и аналитика
*💰 Бюджеты* - Контроль лимитов
*📈 Статистика* - Детальный анализ
*📤 Экспорт* - Выгрузка в Excel

*Быстрый ввод:* "1500 еда обед" или "-50000 зарплата"
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown', 
                                  reply_markup=get_main_menu_keyboard())

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает детальную статистику"""
    user_id = update.message.from_user.id
    
    try:
        stats = analytics_service.get_detailed_stats(user_id)
        
        if not stats['all_time']['income'] and not stats['all_time']['expense']:
            await update.message.reply_text("📊 *Статистика*\n\nНет данных для анализа.", parse_mode='Markdown')
            return
        
        stats_text = f"""
📈 *Детальная статистика*

*Текущий месяц:*
✅ Доходы: {stats['monthly']['income']:,.0f} руб.
❌ Расходы: {stats['monthly']['expense']:,.0f} руб.
💰 Маржа: {stats['monthly']['margin']:,.0f} руб.

*За все время:*
✅ Общие доходы: {stats['all_time']['income']:,.0f} руб.
❌ Общие расходы: {stats['all_time']['expense']:,.0f} руб.
💰 Общая маржа: {stats['all_time']['margin']:,.0f} руб.

*Топ категорий расходов:*
"""
        total_expenses = stats['total_expenses']
        for category, amount in stats['top_expenses'].items():
            percent = (amount / total_expenses * 100) if total_expenses > 0 else 0
            stats_text += f"• {category}: {amount:,.0f} руб. ({percent:.1f}%)\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики.")

async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экспортирует данные в Excel"""
    user_id = update.message.from_user.id
    
    try:
        filename = export_service.export_to_excel(user_id)
        
        if not filename:
            await update.message.reply_text("❌ Нет данных для экспорта.")
            return
        
        await update.message.reply_document(
            document=open(filename, 'rb'),
            filename='finance_export.xlsx'
        )
        
        # Удаляем временный файл
        export_service.cleanup_file(filename)
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        await update.message.reply_text("❌ Ошибка при экспорте данных.")

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает справку"""
    help_text = """
ℹ️ *Помощь по боту*

*Основные функции:*
• 💸 Добавить расход - Внести трату
• 💳 Добавить доход - Внести доход
• 📊 Отчеты - Графики и аналитика
• 💰 Бюджеты - Контроль лимитов
• 📈 Статистика - Детальный анализ
• 📤 Экспорт - Выгрузка в Excel

*Быстрый ввод:*
Просто отправьте сообщение в формате:
`1500 еда обед в кафе` - расход
`-50000 зарплата` - доход (отрицательная сумма)

*Категории расходов:*
🍎 Еда, 🚗 Транспорт, 🎮 Развлечения, 🏠 Коммуналка, 👕 Одежда, 🏥 Здоровье, 📚 Образование
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_menu_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды из главного меню"""
    text = update.message.text
    
    if text == '💸 Добавить расход':
        return await add_expense(update, context)
    elif text == '💳 Добавить доход':
        return await add_income(update, context)
    elif text == '📊 Отчеты и аналитика':
        await show_reports(update, context)
    elif text == '💰 Бюджеты':
        await show_budgets_menu(update, context)
    elif text == '📈 Статистика':
        await show_stats(update, context)
    elif text == '📤 Экспорт данных':
        await export_data(update, context)
    elif text == 'ℹ️ Помощь':
        await show_help(update, context)
    else:
        await quick_input(update, context)

# Импортируем функции после их определения
from .reports_handlers import show_reports
from .budgets_handlers import show_budgets_menu
from .conversations import add_expense, add_income, quick_input