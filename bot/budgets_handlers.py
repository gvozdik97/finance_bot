# finance_bot/bot/budgets_handlers.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.budgets_menu import (
    get_budgets_main_keyboard, 
    get_user_budgets_keyboard,
    get_overwrite_budget_keyboard
)
from keyboards.main_menu import remove_keyboard
from services.budget_service import budget_service
from services.transaction_service import transaction_service

from .common import show_main_menu_from_query

logger = logging.getLogger(__name__)

async def show_budgets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню управления бюджетами"""
    await update.message.reply_text(
        "💰 *Управление бюджетами*", 
        parse_mode='Markdown', 
        reply_markup=get_budgets_main_keyboard()
    )

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает основные действия с бюджетами"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "budget_list":
        await list_budgets(query, context)
    elif query.data == "budget_add":
        await start_add_budget(query, context)
    elif query.data == "budget_edit":
        await start_edit_budget(query, context)
    elif query.data == "budget_delete":
        await start_delete_budget(query, context)

async def list_budgets(query, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список бюджетов пользователя"""
    user_id = query.from_user.id
    budgets = budget_service.get_user_budgets(user_id)
    
    if not budgets:
        await query.message.reply_text("📊 *Ваши бюджеты*\n\nБюджеты не установлены.")
        return
    
    text = "📊 *Ваши бюджеты:*\n\n"
    for budget in budgets:
        period_days = 30 if budget.period == 'monthly' else 7
        spent = transaction_service.get_category_spending(user_id, budget.category, period_days)
        percent = (spent / budget.amount * 100) if budget.amount > 0 else 0
        
        status = "🟢" if percent <= 80 else "🟡" if percent <= 100 else "🔴"
        period_text = "месяц" if budget.period == 'monthly' else "неделя"
        text += f"{status} *{budget.category}*\n"
        text += f"Лимит: {budget.amount:,.0f} руб. ({period_text})\n"
        text += f"Потрачено: {spent:,.0f} руб. ({percent:.1f}%)\n\n"
    
    text += "💡 Используйте кнопки ниже для управления бюджетами"
    await query.message.reply_text(text, parse_mode='Markdown')

async def start_add_budget(query, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс добавления бюджета"""
    from keyboards.budgets_menu import get_budget_categories_keyboard
    await query.message.reply_text(
        "Выберите категорию для бюджета:", 
        reply_markup=get_budget_categories_keyboard()
    )

async def start_edit_budget(query, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс изменения бюджета"""
    user_id = query.from_user.id
    budgets = budget_service.get_user_budgets(user_id)
    
    if not budgets:
        await query.message.reply_text("❌ У вас нет установленных бюджетов для изменения.")
        return
    
    # Подготавливаем данные для клавиатуры
    user_budgets_data = [(budget.category, budget.amount) for budget in budgets]
    keyboard = get_user_budgets_keyboard(user_budgets_data, "edit_budget")
    
    await query.message.reply_text("📋 Выберите бюджет для изменения:", reply_markup=keyboard)

async def start_delete_budget(query, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс удаления бюджета"""
    user_id = query.from_user.id
    budgets = budget_service.get_user_budgets(user_id)
    
    if not budgets:
        await query.message.reply_text("❌ У вас нет установленных бюджетов для удаления.")
        return
    
    # Подготавливаем данные для клавиатуры
    user_budgets_data = [(budget.category, budget.amount) for budget in budgets]
    keyboard = get_user_budgets_keyboard(user_budgets_data, "delete_budget")
    
    await query.message.reply_text("📋 Выберите бюджет для удаления:", reply_markup=keyboard)

# Эти функции будут использоваться в conversation handlers
async def budget_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор категории для бюджета"""
    from utils.constants import BUDGET_AMOUNT
    
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace('budget_cat_', '')
    context.user_data['budget_category'] = category
    context.user_data['budget_period'] = 'monthly'
    
    await query.message.reply_text(
        f"Категория: {category}\nВведите месячный бюджет в рублях:",
        reply_markup=remove_keyboard()
    )
    return BUDGET_AMOUNT

async def delete_budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает удаление бюджета"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_delete":
        await query.message.reply_text("❌ Удаление бюджета отменено.")
        await show_main_menu_from_query(query, context)
        return
    
    category = query.data.replace('delete_budget_', '')
    user_id = query.from_user.id
    
    success = budget_service.delete_budget(user_id, category)
    
    if success:
        await query.message.reply_text(f"✅ Бюджет для категории '{category}' успешно удален!")
    else:
        await query.message.reply_text("❌ Ошибка при удалении бюджета.")
    
    await show_main_menu_from_query(query, context)

async def overwrite_budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает перезапись бюджета"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_overwrite":
        await query.message.reply_text("❌ Создание бюджета отменено.")
        await show_main_menu_from_query(query, context)
        context.user_data.clear()
        return
    
    # Обработка перезаписи
    amount = float(query.data.replace('overwrite_budget_', ''))
    user_id = query.from_user.id
    category = context.user_data['pending_budget']['category']
    
    success = budget_service.update_budget(user_id, category, amount)
    
    if success:
        await query.message.reply_text(
            f"✅ Бюджет обновлен!\n"
            f"• Категория: {category}\n"
            f"• Новый лимит: {amount} руб./месяц"
        )
    else:
        await query.message.reply_text("❌ Ошибка при обновлении бюджета.")
    
    await show_main_menu_from_query(query, context)
    context.user_data.clear()