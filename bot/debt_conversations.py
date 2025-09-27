# bot/debt_conversations.py - ВАВИЛОНСКИЕ ДИАЛОГИ ПО ДОЛГАМ

import logging
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from services.debt_service import debt_service
from services.wallet_service import wallet_service
from keyboards.main_menu import get_main_menu_keyboard, remove_keyboard
from .common import show_main_menu

logger = logging.getLogger(__name__)

# Состояния для диалога добавления долга
DEBT_CREDITOR, DEBT_AMOUNT, DEBT_INTEREST, DEBT_DUE_DATE = range(4)

async def start_add_debt_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает вавилонский диалог добавления долга"""
    await update.message.reply_text(
        "🏛️ *Добавление нового долга*\n\n"
        "💡 *Мудрость Вавилона:* «Лучше маленькая собственность, чем большой долг»\n\n"
        "Введите имя кредитора (банк, друг, организация):",
        parse_mode='Markdown',
        reply_markup=remove_keyboard()
    )
    return DEBT_CREDITOR

async def handle_creditor_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод кредитора"""
    creditor = update.message.text.strip()
    
    if len(creditor) < 2:
        await update.message.reply_text("❌ Имя кредитора слишком короткое. Введите еще раз:")
        return DEBT_CREDITOR
    
    context.user_data['creditor'] = creditor
    
    await update.message.reply_text(
        f"💼 Введите сумму долга для *{creditor}*:\n\n"
        f"Пример: `50000` или `100000`",
        parse_mode='Markdown'
    )
    return DEBT_AMOUNT

async def handle_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод суммы долга"""
    try:
        amount = float(update.message.text.replace(',', '.'))
        
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной. Введите еще раз:")
            return DEBT_AMOUNT
        
        context.user_data['amount'] = amount
        
        await update.message.reply_text(
            "📈 Введите процентную ставку (или 0, если без процентов):\n\n"
            "Пример: `15` для 15% или `0` для беспроцентного",
            reply_markup=remove_keyboard()
        )
        return DEBT_INTEREST
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число. Пример: `50000`")
        return DEBT_AMOUNT

async def handle_interest_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод процентной ставки"""
    try:
        interest_rate = float(update.message.text.replace(',', '.'))
        
        if interest_rate < 0:
            await update.message.reply_text("❌ Ставка не может быть отрицательной. Введите еще раз:")
            return DEBT_INTEREST
        
        context.user_data['interest_rate'] = interest_rate
    
        await update.message.reply_text(
            "📅 Введите дату погашения (дд.мм.гггг) или нажмите /skip:\n\n"
            "Пример: `31.12.2025` или /skip для срока по умолчанию",
            reply_markup=remove_keyboard()
        )
        return DEBT_DUE_DATE
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число. Пример: `15` для 15%")
        return DEBT_INTEREST

async def handle_due_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод даты погашения"""
    due_date_text = update.message.text.strip()
    
    if due_date_text == '/skip':
        context.user_data['due_date'] = None
    else:
        try:
            # Парсим дату в формате дд.мм.гггг
            due_date = datetime.strptime(due_date_text, '%d.%m.%Y')
            context.user_data['due_date'] = due_date
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат даты. Используйте дд.мм.гггг\n"
                "Пример: `31.12.2025` или /skip для пропуска"
            )
            return DEBT_DUE_DATE
    
    return await save_debt(update, context)

async def skip_due_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропускает ввод даты погашения"""
    context.user_data['due_date'] = None
    return await save_debt(update, context)

async def save_debt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет долг и показывает вавилонскую мудрость"""
    user_data = context.user_data
    user_id = update.message.from_user.id
    
    try:
        result = debt_service.add_debt(
            user_id=user_id,
            creditor=user_data['creditor'],
            amount=user_data['amount'],
            interest_rate=user_data.get('interest_rate', 0.0),
            due_date=user_data.get('due_date')
        )
        
        if result['success']:
            await update.message.reply_text(result['message'], parse_mode='Markdown')
            
            # Обновляем прогресс правила "Свобода от долгов"
            await update_debt_rule_progress(user_id)
            
        else:
            await update.message.reply_text(f"❌ {result['error']}")
    
    except Exception as e:
        logger.error(f"Save debt error: {e}")
        await update.message.reply_text("❌ Ошибка при сохранении долга.")
    
    # Возвращаем в главное меню
    await show_main_menu(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def update_debt_rule_progress(user_id: int):
    """Обновляет прогресс правила 'Свобода от долгов'"""
    debts = debt_service.get_active_debts(user_id)
    
    if not debts:
        # Нет долгов - правило выполнено на 100%
        from services.babylon_service import babylon_service
        babylon_service.update_rule_progress(user_id, 'debt_free', 100.0)
    else:
        # Прогресс основан на уменьшении общей суммы долгов
        total_debt = sum(debt.current_amount for debt in debts)
        # Чем меньше долг, тем выше прогресс (упрощенная логика)
        progress = max(0.0, min(100.0, (1 - (total_debt / (total_debt + 10000))) * 100))
        from services.babylon_service import babylon_service
        babylon_service.update_rule_progress(user_id, 'debt_free', progress)

# ============================================================================
# БЫСТРЫЙ ВВОД ДОЛГОВ
# ============================================================================

async def quick_debt_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрый ввод долга в одну строку"""
    text = update.message.text.strip()
    
    # Паттерн: "Долг Кредитор Сумма [Процент] [Дата]"
    pattern = r'долг\s+(\w+)\s+(\d+)(?:\s+(\d+))?(?:\s+(\d{2}\.\d{2}\.\d{4}))?'
    match = re.search(pattern, text.lower())
    
    if not match:
        await update.message.reply_text(
            "❌ *Формат быстрого ввода долга:*\n"
            "`долг Банк 50000 15 31.12.2025`\n\n"
            "• Обязательно: кредитор и сумма\n"
            "• Опционально: процент и дата",
            parse_mode='Markdown'
        )
        return
    
    creditor = match.group(1).title()
    amount = float(match.group(2))
    interest_rate = float(match.group(3)) if match.group(3) else 0.0
    due_date_text = match.group(4)
    
    try:
        due_date = datetime.strptime(due_date_text, '%d.%m.%Y') if due_date_text else None
        
        user_id = update.message.from_user.id
        result = debt_service.add_debt(user_id, creditor, amount, interest_rate, due_date)
        
        if result['success']:
            await update.message.reply_text(result['message'], parse_mode='Markdown')
            await update_debt_rule_progress(user_id)
        else:
            await update.message.reply_text(f"❌ {result['error']}")
            
    except ValueError:
        await update.message.reply_text("❌ Ошибка в формате даты. Используйте дд.мм.гггг")
    except Exception as e:
        logger.error(f"Quick debt input error: {e}")
        await update.message.reply_text("❌ Ошибка при быстром добавлении долга.")

# ============================================================================
# CONVERSATION HANDLER ДЛЯ ДОЛГОВ
# ============================================================================

def create_debt_conversation_handler():
    """Создает обработчик диалога добавления долга"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^➕ Добавить долг$'), start_add_debt_flow)
        ],
        states={
            DEBT_CREDITOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_creditor_input)],
            DEBT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount_input)],
            DEBT_INTEREST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interest_input)],
            DEBT_DUE_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_due_date_input),
                CommandHandler('skip', skip_due_date)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_debt_conversation)],
        allow_reentry=True
    )

async def cancel_debt_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет диалог добавления долга"""
    await update.message.reply_text(
        "❌ Добавление долга отменено.",
        reply_markup=get_main_menu_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

__all__ = [
    'start_add_debt_flow', 'quick_debt_input', 'create_debt_conversation_handler'
]