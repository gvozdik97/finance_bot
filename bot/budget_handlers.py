# bot/budget_handlers.py - ОБНОВЛЯЕМ С ПОДТВЕРЖДЕНИЕМ ДУБЛИКАТОВ
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from services.budget_planner import budget_planner
from services.simple_budget_service import simple_budget_service
from keyboards.budget_menu import get_budget_management_keyboard, get_budget_categories_keyboard, get_budget_confirmation_keyboard
from keyboards.main_menu import get_main_menu_keyboard, remove_keyboard
from .common import show_main_menu

logger = logging.getLogger(__name__)

# Состояния для диалога установки бюджета
BUDGET_CATEGORY, BUDGET_AMOUNT, BUDGET_CONFIRMATION = range(10, 13)

async def show_budgets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню управления бюджетами"""
    menu_text = """
💰 *УПРАВЛЕНИЕ БЮДЖЕТАМИ*

Планируйте и контролируйте свои расходы:

• 💰 Мои бюджеты - текущие лимиты и прогресс
• 🎯 Установить бюджет - создать новый лимит
• 💡 Рекомендации - умные предложения

💡 *Совет Вавилона:* «Мудрый человек знает меру в расходах»
"""
    await update.message.reply_text(
        menu_text,
        parse_mode='Markdown',
        reply_markup=get_budget_management_keyboard()
    )

async def show_my_budgets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает установленные бюджеты и прогресс"""
    user_id = update.message.from_user.id
    
    try:
        progress = budget_planner.get_budget_progress(user_id)
        
        if not progress['success']:
            await update.message.reply_text(
                f"❌ {progress['error']}",
                reply_markup=get_budget_management_keyboard()
            )
            return
        
        if not progress['has_budgets']:
            await update.message.reply_text(
                progress['message'],
                parse_mode='Markdown',
                reply_markup=get_budget_management_keyboard()
            )
            return
        
        budgets_text = "💰 *ВАШИ БЮДЖЕТЫ*\n\n"
        
        for budget in progress['budgets']:
            # Создаем прогресс-бар
            bar_length = int(budget['percentage'] / 10)
            bar = '█' * bar_length + '░' * (10 - bar_length)
            
            budgets_text += f"**{budget['category']}** {budget['status']}\n"
            budgets_text += f"Лимит: {budget['budget']:,.0f} руб.\n"
            budgets_text += f"Потрачено: {budget['spent']:,.0f} руб. ({budget['percentage']:.1f}%)\n"
            budgets_text += f"Осталось: {budget['remaining']:,.0f} руб.\n"
            budgets_text += f"{bar}\n\n"
        
        # Общая статистика
        budgets_text += f"📊 *ОБЩАЯ СТАТИСТИКА:*\n"
        budgets_text += f"Всего бюджетов: {len(progress['budgets'])}\n"
        budgets_text += f"Общий лимит: {progress['total_budget']:,.0f} руб.\n"
        budgets_text += f"Всего потрачено: {progress['total_spent']:,.0f} руб.\n"
        budgets_text += f"Использовано: {progress['overall_percentage']:.1f}%\n\n"
        
        # Уведомления
        if progress['alerts']:
            budgets_text += "⚠️ *УВЕДОМЛЕНИЯ:*\n"
            for alert in progress['alerts']:
                budgets_text += f"• {alert}\n"
        
        await update.message.reply_text(
            budgets_text,
            parse_mode='Markdown',
            reply_markup=get_budget_management_keyboard()
        )
        
    except Exception as e:
        logger.error(f"My budgets error: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении бюджетов",
            reply_markup=get_budget_management_keyboard()
        )

async def start_set_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс установки бюджета"""
    await update.message.reply_text(
        "🎯 *Установка месячного бюджета*\n\n"
        "Выберите категорию для установки лимита:",
        parse_mode='Markdown',
        reply_markup=get_budget_categories_keyboard()
    )
    return BUDGET_CATEGORY

async def handle_budget_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор категории для бюджета"""
    category = update.message.text.strip()
    
    if category == '🏠 Главное меню':
        await show_main_menu(update, context)
        return ConversationHandler.END
    
    context.user_data['budget_category'] = category
    
    # Проверяем существующий бюджет
    user_id = update.message.from_user.id
    existing_budget = budget_planner.check_existing_budget(user_id, category)
    
    if existing_budget is not None:
        context.user_data['existing_budget'] = existing_budget
        await update.message.reply_text(
            f"⚠️ *Бюджет уже установлен!*\n\n"
            f"Категория: **{category}**\n"
            f"Текущий лимит: {existing_budget:,.0f} руб.\n\n"
            f"Хотите перезаписать бюджет?",
            parse_mode='Markdown',
            reply_markup=get_budget_confirmation_keyboard()
        )
        return BUDGET_CONFIRMATION
    else:
        await update.message.reply_text(
            f"📊 *Установка бюджета для: {category}*\n\n"
            f"Введите месячный лимит в рублях:\n\n"
            f"Пример: `5000` или `15000`",
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return BUDGET_AMOUNT

async def handle_budget_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает подтверждение перезаписи бюджета"""
    response = update.message.text.strip()
    
    if response == '✅ Да, перезаписать':
        await update.message.reply_text(
            f"📊 *Установка бюджета для: {context.user_data['budget_category']}*\n\n"
            f"Введите новый месячный лимит в рублях:\n\n"
            f"Пример: `5000` или `15000`",
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return BUDGET_AMOUNT
    elif response in ['❌ Нет, отменить', '🏠 Главное меню']:
        await update.message.reply_text(
            "❌ Установка бюджета отменена.",
            reply_markup=get_budget_management_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, выберите вариант из меню:",
            reply_markup=get_budget_confirmation_keyboard()
        )
        return BUDGET_CONFIRMATION

async def handle_budget_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод суммы бюджета"""
    try:
        amount = float(update.message.text.replace(',', '.'))
        
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной. Введите еще раз:")
            return BUDGET_AMOUNT
        
        user_id = update.message.from_user.id
        category = context.user_data['budget_category']
        
        result = budget_planner.set_monthly_budget(user_id, category, amount)
        
        if result['success']:
            await update.message.reply_text(
                result['message'],
                parse_mode='Markdown',
                reply_markup=get_budget_management_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ {result['error']}",
                reply_markup=get_budget_management_keyboard()
            )
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число. Пример: `5000`")
        return BUDGET_AMOUNT

async def show_budget_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает рекомендации по бюджетам"""
    user_id = update.message.from_user.id
    
    try:
        suggestions = budget_planner.suggest_budgets(user_id)
        
        if not suggestions['success']:
            await update.message.reply_text(
                f"❌ {suggestions['error']}",
                reply_markup=get_budget_management_keyboard()
            )
            return
        
        if not suggestions['has_suggestions']:
            await update.message.reply_text(
                suggestions['message'],
                parse_mode='Markdown',
                reply_markup=get_budget_management_keyboard()
            )
            return
        
        recommendations_text = "💡 *РЕКОМЕНДАЦИИ ПО БЮДЖЕТАМ*\n\n"
        recommendations_text += "На основе вашей истории расходов:\n\n"
        
        for suggestion in suggestions['suggestions']:
            recommendations_text += f"**{suggestion['category']}**\n"
            recommendations_text += f"Средние расходы: {suggestion['avg_spending']:,.0f} руб./мес\n"
            recommendations_text += f"💡 Рекомендуемый бюджет: {suggestion['suggested_budget']:,.0f} руб./мес\n"
            recommendations_text += f"📈 {suggestion['reasoning']}\n\n"
        
        recommendations_text += "💎 *Совет:* Установите бюджеты для лучшего контроля!"
        
        await update.message.reply_text(
            recommendations_text,
            parse_mode='Markdown',
            reply_markup=get_budget_management_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Budget recommendations error: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении рекомендаций",
            reply_markup=get_budget_management_keyboard()
        )

async def handle_budget_menu_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды меню бюджетирования"""
    text = update.message.text
    
    if text == '💰 Мои бюджеты':
        await show_my_budgets(update, context)
    elif text == '🎯 Установить бюджет':
        return await start_set_budget(update, context)
    elif text == '💡 Рекомендации':
        await show_budget_recommendations(update, context)
    elif text == '🏠 Главное меню':
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "❌ Команда не распознана",
            reply_markup=get_budget_management_keyboard()
        )

async def cancel_budget_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет диалог установки бюджета"""
    await update.message.reply_text(
        "❌ Установка бюджета отменена.",
        reply_markup=get_budget_management_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

def create_budget_conversation_handler():
    """Создает обработчик диалога установки бюджета"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^🎯 Установить бюджет$'), start_set_budget)
        ],
        states={
            BUDGET_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget_category)],
            BUDGET_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget_confirmation)],
            BUDGET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel_budget_conversation)],
        allow_reentry=True
    )