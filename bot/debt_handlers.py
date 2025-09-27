# bot/debt_handlers.py - ПОЛНАЯ РЕАЛИЗАЦИЯ ВСЕХ ФУНКЦИЙ

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from services.debt_service import debt_service
from services.wallet_service import wallet_service
from keyboards.main_menu import get_main_menu_keyboard, remove_keyboard
from keyboards.debt_menu import get_debt_management_keyboard, get_debt_selection_keyboard
from .common import show_main_menu

logger = logging.getLogger(__name__)

# Состояния для диалога погашения долга
SELECT_DEBT, ENTER_PAYMENT_AMOUNT = range(2)

# ============================================================================
# ОСНОВНЫЕ ФУНКЦИИ ОТОБРАЖЕНИЯ
# ============================================================================

async def show_debts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список долгов"""
    user_id = update.message.from_user.id
    
    try:
        debts = debt_service.get_active_debts(user_id)
        
        if not debts:
            await update.message.reply_text(
                "🎉 *У вас нет активных долгов!*\n\n"
                "💡 *Мудрость Вавилона:* «Свободный от долгов человек — уже богач!»",
                parse_mode='Markdown',
                reply_markup=get_debt_management_keyboard()
            )
            return
        
        debts_text = "📜 *Ваши активные долги:*\n\n"
        total_debt = 0
        
        for i, debt in enumerate(debts, 1):
            interest_info = f" ({debt.interest_rate}%)" if debt.interest_rate > 0 else ""
            due_info = f" до {debt.due_date.strftime('%d.%m.%Y')}" if debt.due_date else ""
            debts_text += f"{i}. *{debt.creditor}*: {debt.current_amount:,.0f} руб.{interest_info}{due_info}\n"
            total_debt += debt.current_amount
        
        debts_text += f"\n💰 *Общая сумма долгов:* {total_debt:,.0f} руб."
        debts_text += f"\n📋 *Количество долгов:* {len(debts)}"
        
        await update.message.reply_text(
            debts_text, 
            parse_mode='Markdown',
            reply_markup=get_debt_management_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Debts menu error: {e}")
        await update.message.reply_text("❌ Ошибка при получении списка долгов.")

async def show_snowball_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает план погашения по методу снежного кома"""
    user_id = update.message.from_user.id
    
    try:
        plan = debt_service.calculate_snowball_plan(user_id)
        
        if not plan['has_debts']:
            await update.message.reply_text(
                plan['message'], 
                parse_mode='Markdown',
                reply_markup=get_debt_management_keyboard()
            )
            return
        
        plan_text = "📋 *План погашения долгов (Метод снежного кома)*\n\n"
        plan_text += f"💰 *Общая сумма долгов:* {plan['total_debt']:,.0f} руб.\n\n"
        
        plan_text += "🎯 *Рекомендуемая последовательность:*\n"
        for item in plan['plan']:
            plan_text += f"🥇 *{item['priority']}. {item['creditor']}*\n"
            plan_text += f"   💰 Сумма: {item['amount']:,.0f} руб.\n"
            plan_text += f"   💳 Рекомендуемый платеж: {item['recommended_payment']:,.0f} руб.\n\n"
        
        plan_text += "💡 *Совет Вавилона:* «Начинайте с малых долгов — каждая победа придает сил для больших сражений!»"
        
        await update.message.reply_text(
            plan_text, 
            parse_mode='Markdown',
            reply_markup=get_debt_management_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Snowball plan error: {e}")
        await update.message.reply_text("❌ Ошибка при расчете плана погашения.")

async def show_debt_freedom_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает прогресс освобождения от долгов"""
    user_id = update.message.from_user.id
    
    try:
        debts = debt_service.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        
        if total_debt == 0:
            progress_text = "🎊 *🏛️ ДВЕРЬ В ВАВИЛОНСКИЙ ХРАМ ОТКРЫТА!* 🎊\n\n"
            progress_text += "💎 *Мудрость Вавилона:* \n"
            progress_text += "«Свободный от долгов человек подобен царю! \n"
            progress_text += "Теперь ваши деньги работают на вас, \n"
            progress_text += "а не вы на свои долги.»"
        else:
            initial_debt = sum(debt.initial_amount for debt in debts)
            progress = ((initial_debt - total_debt) / initial_debt * 100) if initial_debt > 0 else 0
            
            # Прогресс-бар
            filled = '█' * int(progress / 10)
            empty = '░' * (10 - int(progress / 10))
            progress_bar = f"{filled}{empty}"
            
            progress_text = f"📈 *ПУТЬ К СВОБОДЕ ОТ ДОЛГОВ*\n\n"
            progress_text += f"🏛️ *Прогресс:* {progress:.1f}%\n"
            progress_text += f"{progress_bar}\n\n"
            progress_text += f"💰 Начальная сумма: {initial_debt:,.0f} руб.\n"
            progress_text += f"🎯 Текущий долг: {total_debt:,.0f} руб.\n"
            progress_text += f"✅ Погашено: {initial_debt - total_debt:,.0f} руб.\n\n"
            progress_text += "💡 *Совет Вавилона:* «Каждый платеж приближает вас к финансовой свободе!»"
        
        await update.message.reply_text(
            progress_text, 
            parse_mode='Markdown',
            reply_markup=get_debt_management_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Debt progress error: {e}")
        await update.message.reply_text("❌ Ошибка при создании прогресса.")

async def show_debt_milestones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает вехи освобождения от долгов"""
    user_id = update.message.from_user.id
    
    try:
        debts = debt_service.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        initial_debt = sum(debt.initial_amount for debt in debts)
        
        if total_debt == 0:
            milestones_text = "🏆 *Поздравляем! Вы достигли полной финансовой свободы!*"
        else:
            progress = ((initial_debt - total_debt) / initial_debt * 100) if initial_debt > 0 else 0
            
            milestones_text = "🎯 *Вехи освобождения от долгов*\n\n"
            
            milestones = [
                (25, "🥉 Бронзовый уровень", "Первый серьезный прогресс!"),
                (50, "🥈 Серебряный уровень", "Половина пути пройдена!"),
                (75, "🥇 Золотой уровень", "Осталось совсем немного!"),
                (100, "🏆 Полная свобода", "Вы достигли финансовой свободы!")
            ]
            
            for threshold, title, description in milestones:
                if progress >= threshold:
                    status = "✅ ДОСТИГНУТО"
                else:
                    status = "⏳ В ПРОЦЕССЕ"
                
                milestones_text += f"{title} - {status}\n"
                milestones_text += f"   {description}\n\n"
            
            milestones_text += f"📊 *Текущий прогресс:* {progress:.1f}%"
        
        await update.message.reply_text(
            milestones_text, 
            parse_mode='Markdown',
            reply_markup=get_debt_management_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Debt milestones error: {e}")
        await update.message.reply_text("❌ Ошибка при получении вех.")

async def show_debt_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику по долгам"""
    user_id = update.message.from_user.id
    
    try:
        stats = debt_service.get_debt_statistics(user_id)
        
        stats_text = "📊 *Статистика долгов*\n\n"
        
        if stats['total_debt'] == 0:
            stats_text += "🎉 *Поздравляем! У вас нет долгов!*\n\n"
            stats_text += "💡 *Мудрость Вавилона:* «Свободный от долгов человек подобен царю!»"
        else:
            stats_text += f"💰 *Общая сумма долгов:* {stats['total_debt']:,.0f} руб.\n"
            stats_text += f"📋 *Количество долгов:* {stats['debt_count']}\n"
            stats_text += f"💼 *Баланс бюджета:* {stats['budget_balance']:,.0f} руб.\n"
            stats_text += f"⚖️ *Соотношение долг/бюджет:* {stats['debt_to_budget_ratio']:.1f}%\n"
            stats_text += f"📈 *Уровень риска:* {stats['risk_level']}\n"
            stats_text += f"⏱️ *Примерное время погашения:* {stats['estimated_payoff_time']}\n\n"
            stats_text += f"💡 *Рекомендация:* {stats['recommendation']}"
        
        await update.message.reply_text(
            stats_text, 
            parse_mode='Markdown',
            reply_markup=get_debt_management_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Debt statistics error: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики долгов.")

# ============================================================================
# ДИАЛОГ ПОГАШЕНИЯ ДОЛГА
# ============================================================================

async def start_payment_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс погашения долга"""
    user_id = update.message.from_user.id
    debts = debt_service.get_active_debts(user_id)
    
    if not debts:
        await update.message.reply_text(
            "🎉 У вас нет активных долгов для погашения!",
            reply_markup=get_debt_management_keyboard()
        )
        return ConversationHandler.END
    
    budget_balance = wallet_service.get_wallet_balance(user_id, 'living_budget')
    
    if budget_balance <= 0:
        await update.message.reply_text(
            "🚫 *Недостаточно средств для погашения долгов!*\n\n"
            f"💼 Баланс Бюджета на жизнь: {budget_balance:,.0f} руб.\n\n"
            f"💡 *Совет Вавилона:* «Сначала наполни кошелек, потом плати долги»",
            parse_mode='Markdown',
            reply_markup=get_debt_management_keyboard()
        )
        return ConversationHandler.END
    
    debts_text = f"💳 *Погашение долгов*\n\n"
    debts_text += f"💼 *Доступно в бюджете:* {budget_balance:,.0f} руб.\n\n"
    debts_text += "📋 *Выберите долг для погашения:*\n\n"
    
    for i, debt in enumerate(debts, 1):
        urgency = ""
        if debt.due_date and debt.due_date < datetime.now() + timedelta(days=30):
            urgency = " 🔥"
        debts_text += f"{i}. {debt.creditor} - {debt.current_amount:,.0f} руб.{urgency}\n"
    
    context.user_data['debts_list'] = debts
    context.user_data['available_budget'] = budget_balance
    
    await update.message.reply_text(
        debts_text, 
        parse_mode='Markdown',
        reply_markup=get_debt_selection_keyboard(debts)
    )
    return SELECT_DEBT

async def handle_debt_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор долга для погашения"""
    try:
        if update.message.text == '🔙 Назад к долгам':
            await show_debts_main_menu(update, context)
            context.user_data.clear()
            return ConversationHandler.END
        
        debt_number = int(update.message.text.split('.')[0])
        debts = context.user_data['debts_list']
        
        if debt_number < 1 or debt_number > len(debts):
            await update.message.reply_text("❌ Неверный номер долга. Введите еще раз:")
            return SELECT_DEBT
        
        selected_debt = debts[debt_number - 1]
        context.user_data['selected_debt'] = selected_debt
        context.user_data['selected_debt_id'] = selected_debt.id
        
        available_budget = context.user_data['available_budget']
        
        await update.message.reply_text(
            f"🏛️ *Погашение долга: {selected_debt.creditor}*\n\n"
            f"💼 Текущая сумма: {selected_debt.current_amount:,.0f} руб.\n"
            f"💳 Доступно для погашения: {available_budget:,.0f} руб.\n\n"
            f"Введите сумму платежа:",
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return ENTER_PAYMENT_AMOUNT
        
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Пожалуйста, введите номер долга:")
        return SELECT_DEBT

async def handle_payment_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод суммы платежа"""
    try:
        payment_amount = float(update.message.text.replace(',', '.'))
        selected_debt = context.user_data['selected_debt']
        available_budget = context.user_data['available_budget']
        user_id = update.message.from_user.id
        
        if payment_amount <= 0:
            await update.message.reply_text("❌ Сумма платежа должна быть положительной. Введите еще раз:")
            return ENTER_PAYMENT_AMOUNT
        
        if payment_amount > available_budget:
            await update.message.reply_text(
                f"🚫 *Сумма превышает доступный бюджет!*\n\n"
                f"💼 Доступно: {available_budget:,.0f} руб.\n"
                f"💸 Запрошено: {payment_amount:,.0f} руб.\n\n"
                f"Введите меньшую сумму:",
                parse_mode='Markdown'
            )
            return ENTER_PAYMENT_AMOUNT
        
        if payment_amount > selected_debt.current_amount:
            await update.message.reply_text(
                f"💡 *Сумма превышает остаток долга!*\n\n"
                f"📋 Остаток долга: {selected_debt.current_amount:,.0f} руб.\n"
                f"💳 Будет списано: {selected_debt.current_amount:,.0f} руб.\n\n"
                f"Продолжить? (да/нет)",
                parse_mode='Markdown'
            )
            context.user_data['suggested_full_payment'] = True
            return ENTER_PAYMENT_AMOUNT
        
        result = debt_service.make_payment(user_id, selected_debt.id, payment_amount)
        
        if result['success']:
            await update.message.reply_text(result['message'], parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ {result['error']}")
        
        await show_debts_main_menu(update, context)
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число. Пример: `5000`")
        return ENTER_PAYMENT_AMOUNT

async def handle_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает подтверждение полного погашения"""
    response = update.message.text.lower()
    user_id = update.message.from_user.id
    
    if response in ['да', 'yes', 'ок', 'хорошо']:
        selected_debt = context.user_data['selected_debt']
        payment_amount = selected_debt.current_amount
        
        result = debt_service.make_payment(user_id, selected_debt.id, payment_amount)
        
        if result['success']:
            await update.message.reply_text(result['message'], parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ {result['error']}")
    else:
        await update.message.reply_text("Введите сумму платежа заново:")
        return ENTER_PAYMENT_AMOUNT
    
    await show_debts_main_menu(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_debt_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет диалог погашения долга"""
    await update.message.reply_text(
        "❌ Погашение долга отменено.",
        reply_markup=get_debt_management_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

async def show_debts_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает главное меню управления долгами"""
    user_id = update.message.from_user.id
    debts = debt_service.get_active_debts(user_id)
    
    menu_text = "🏛️ *Управление Долгами*\n\n"
    
    if not debts:
        menu_text += "🎉 *У вас нет активных долгов!*\n\n"
        menu_text += "💡 *Мудрость Вавилона:* «Свободный от долгов человек — уже богач!»"
    else:
        total_debt = sum(debt.current_amount for debt in debts)
        menu_text += f"📊 *Общая сумма долгов:* {total_debt:,.0f} руб.\n"
        menu_text += f"📋 *Количество долгов:* {len(debts)}\n\n"
        menu_text += "💡 *Выберите действие из меню ниже:*"
    
    await update.message.reply_text(
        menu_text, 
        parse_mode='Markdown',
        reply_markup=get_debt_management_keyboard()
    )

def create_debt_payment_conversation_handler():
    """Создает обработчик диалога погашения долга"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^💳 Погасить долг$'), start_payment_flow)
        ],
        states={
            SELECT_DEBT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_debt_selection)],
            ENTER_PAYMENT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_amount),
                MessageHandler(filters.Regex(r'^(да|yes|нет|no)$'), handle_payment_confirmation)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_debt_payment)],
        allow_reentry=True
    )