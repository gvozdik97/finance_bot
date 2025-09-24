# finance_bot/bot/conversations.py

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from utils.constants import AMOUNT, CATEGORY, DESCRIPTION, BUDGET_AMOUNT, EDIT_BUDGET_AMOUNT
from utils.validators import validate_amount, validate_budget_amount
from utils.categorizers import clean_category_name, categorize_expense, categorize_income
from utils.formatters import format_transaction_message

from services.transaction_service import transaction_service
from services.budget_service import budget_service

from keyboards.main_menu import get_main_menu_keyboard, get_category_keyboard, remove_keyboard

from .common import show_main_menu, show_main_menu_from_query

logger = logging.getLogger(__name__)

# ============================================================================
# ОБРАБОТЧИКИ ДЛЯ ДОБАВЛЕНИЯ ТРАНЗАКЦИЙ
# ============================================================================

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс добавления расхода"""
    await update.message.reply_text(
        "💸 *Добавление расхода*\n\nВведите сумму:",
        parse_mode='Markdown',
        reply_markup=remove_keyboard()
    )
    context.user_data['type'] = 'expense'
    return AMOUNT

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс добавления дохода"""
    await update.message.reply_text(
        "💳 *Добавление дохода*\n\nВведите сумму:",
        parse_mode='Markdown', 
        reply_markup=remove_keyboard()
    )
    context.user_data['type'] = 'income'
    return AMOUNT

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод суммы"""
    is_valid, result = validate_amount(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(result)
        return AMOUNT
    
    amount = result
    context.user_data['amount'] = amount
    
    # Выбор категории
    transaction_type = context.user_data['type']
    type_text = "расхода" if transaction_type == 'expense' else "дохода"
    
    await update.message.reply_text(
        f"Выберите категорию {type_text}:",
        reply_markup=get_category_keyboard(transaction_type)
    )
    return CATEGORY

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор категории"""
    category = clean_category_name(update.message.text)
    context.user_data['category'] = category
    
    await update.message.reply_text(
        "📝 Введите описание (или нажмите /skip для пропуска):",
        reply_markup=remove_keyboard()
    )
    return DESCRIPTION

async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропускает ввод описания"""
    return await save_transaction(update, context, description="Без описания")

async def save_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE, description: str = None):
    """Сохраняет транзакцию в базу данных"""
    user_data = context.user_data
    
    if description is None:
        description = update.message.text if update.message and update.message.text != '/skip' else "Без описания"
    
    user_id = update.message.from_user.id
    success = transaction_service.add_transaction(
        user_id=user_id,
        transaction_type=user_data['type'],
        amount=user_data['amount'],
        category=user_data['category'],
        description=description
    )
    
    if success:
        message_text = format_transaction_message(
            user_data['type'], 
            user_data['amount'], 
            user_data['category'], 
            description
        )
        await update.message.reply_text(message_text, parse_mode='Markdown')
        
        # Проверка бюджета для расходов
        if user_data['type'] == 'expense':
            await check_budget(update, context, user_data['category'], user_data['amount'])
    else:
        await update.message.reply_text("❌ Ошибка при сохранении транзакции.")
    
    # Возврат в главное меню
    await show_main_menu(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def check_budget(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, amount: float):
    """Проверяет превышение бюджета"""
    user_id = update.message.from_user.id
    budget_check = budget_service.check_budget_exceeded(user_id, category, amount)
    
    if budget_check['exceeded']:
        await update.message.reply_text(
            f"⚠️ *Превышение бюджета!*\n"
            f"Категория: {category}\n"
            f"Лимит: {budget_check['budget_amount']:,.0f} руб.\n"
            f"Будет потрачено: {budget_check['total_after_transaction']:.0f} руб.\n"
            f"Превышение: {budget_check['overspend']:.0f} руб.",
            parse_mode='Markdown'
        )

# ============================================================================
# ОБРАБОТЧИКИ ДЛЯ БЮДЖЕТОВ
# ============================================================================

async def budget_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод суммы бюджета"""
    is_valid, result = validate_budget_amount(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(result)
        return BUDGET_AMOUNT
    
    amount = result
    user_id = update.message.from_user.id
    category = context.user_data['budget_category']
    
    # Проверяем существующий бюджет
    existing_budget = budget_service.get_budget(user_id, category)
    
    if existing_budget:
        # Предлагаем выбор: перезаписать или отменить
        from keyboards.budgets_menu import get_overwrite_budget_keyboard
        await update.message.reply_text(
            f"⚠️ Бюджет для категории '{category}' уже установлен!\n"
            f"• Текущий лимит: {existing_budget.amount} руб.\n"
            f"• Новый лимит: {amount} руб.\n\n"
            f"Хотите перезаписать существующий бюджет?",
            reply_markup=get_overwrite_budget_keyboard(amount)
        )
        
        # Сохраняем данные для возможной перезаписи
        context.user_data['pending_budget'] = {
            'category': category,
            'amount': amount
        }
        
        return ConversationHandler.END
    
    # Если бюджета нет - добавляем новый
    success = budget_service.add_budget(user_id, category, amount, 'monthly')
    
    if success:
        await update.message.reply_text(
            f"✅ Бюджет установлен!\n"
            f"• Категория: {category}\n"
            f"• Лимит: {amount} руб./месяц"
        )
    else:
        await update.message.reply_text("❌ Ошибка при установке бюджета.")
    
    await show_main_menu(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def edit_budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает начало изменения бюджета"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_edit":
        await query.message.reply_text("❌ Изменение бюджета отменено.")
        return ConversationHandler.END
    
    category = query.data.replace('edit_budget_', '')
    
    # Получаем текущий бюджет
    user_id = query.from_user.id
    budget = budget_service.get_budget(user_id, category)
    
    if not budget:
        await query.message.reply_text("❌ Бюджет не найден.")
        return ConversationHandler.END
    
    # Сохраняем данные в context
    context.user_data['edit_budget'] = {
        'category': category,
        'current_amount': budget.amount
    }
    
    await query.message.reply_text(
        f"✏️ *Изменение бюджета*\n\n"
        f"Категория: {category}\n"
        f"Текущий лимит: {budget.amount} руб.\n\n"
        f"Введите новый лимит в рублях:",
        parse_mode='Markdown',
        reply_markup=remove_keyboard()
    )
    
    return EDIT_BUDGET_AMOUNT

async def edit_budget_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод новой суммы бюджета"""
    is_valid, result = validate_budget_amount(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(result)
        return EDIT_BUDGET_AMOUNT
    
    new_amount = result
    user_data = context.user_data.get('edit_budget', {})
    category = user_data.get('category')
    current_amount = user_data.get('current_amount')
    
    if not category:
        await update.message.reply_text("❌ Ошибка: категория не найдена.")
        context.user_data.clear()
        return ConversationHandler.END
    
    user_id = update.message.from_user.id
    
    # Обновляем бюджет
    success = budget_service.update_budget(user_id, category, new_amount)
    
    if success:
        await update.message.reply_text(
            f"✅ Бюджет обновлен!\n\n"
            f"• Категория: {category}\n"
            f"• Старый лимит: {current_amount} руб.\n"
            f"• Новый лимит: {new_amount} руб.\n"
            f"• Изменение: {new_amount - current_amount:+.0f} руб."
        )
    else:
        await update.message.reply_text("❌ Ошибка при обновлении бюджета.")
    
    await show_main_menu(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает отмену изменения бюджета"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("❌ Изменение бюджета отменено.")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду отмены изменения бюджета"""
    await update.message.reply_text("❌ Изменение бюджета отменено.")
    context.user_data.clear()
    return ConversationHandler.END

# ============================================================================
# БЫСТРЫЙ ВВОД
# ============================================================================

async def quick_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает быстрый ввод транзакций"""
    text = update.message.text
    words = text.split()
    
    try:
        if len(words) >= 2:
            amount = float(words[0])
            category_word = words[1].lower()
            description = ' '.join(words[2:]) if len(words) > 2 else "Быстрый ввод"
            
            # Определяем тип и категорию
            if amount < 0:
                transaction_type = 'income'
                amount = abs(amount)
                category = categorize_income(category_word)
            else:
                transaction_type = 'expense'
                category = categorize_expense(category_word)
            
            # Сохраняем транзакцию
            user_id = update.message.from_user.id
            success = transaction_service.add_transaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                category=category,
                description=description
            )
            
            if success:
                # Проверка бюджета для расходов
                if transaction_type == 'expense':
                    budget_check = budget_service.check_budget_exceeded(user_id, category, amount)
                    if budget_check['exceeded']:
                        await update.message.reply_text(
                            f"⚠️ *Превышение бюджета!*\n"
                            f"Категория: {category}\n"
                            f"Лимит: {budget_check['budget_amount']:,.0f} руб.\n"
                            f"Превышение: {budget_check['overspend']:.0f} руб.",
                            parse_mode='Markdown'
                        )
                
                type_text = "Доход" if transaction_type == 'income' else "Расход"
                emoji = "💳" if transaction_type == 'income' else "💸"
                
                await update.message.reply_text(
                    f"{emoji} *{type_text} добавлен!*\n\n"
                    f"• Сумма: {amount} руб.\n"
                    f"• Категория: {category}\n"
                    f"• Описание: {description}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("❌ Ошибка при сохранении транзакции.")
                
    except ValueError:
        await update.message.reply_text("❌ Формат: сумма категория [описание]")

# ============================================================================
# СОЗДАНИЕ CONVERSATION HANDLERS
# ============================================================================

def create_transaction_conversation_handler():
    """Создает ConversationHandler для добавления транзакций"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(💸 Добавить расход|💳 Добавить доход)$'), 
                          lambda update, context: handle_transaction_start(update, context))
        ],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_handler)],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, 
                             lambda update, context: save_transaction(update, context)),
                CommandHandler('skip', skip_description)
            ]
        },
        fallbacks=[],
    )

def create_budget_conversation_handler():
    """Создает ConversationHandler для добавления бюджетов"""
    from .budgets_handlers import budget_category_handler
    
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(budget_category_handler, pattern='^budget_cat_')],
        states={
            BUDGET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget_amount_handler)]
        },
        fallbacks=[],
    )

def create_edit_budget_conversation_handler():
    """Создает ConversationHandler для изменения бюджетов"""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_budget_handler, pattern='^edit_budget_')],
        states={
            EDIT_BUDGET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_budget_amount_handler)]
        },
        fallbacks=[
            CallbackQueryHandler(cancel_edit_handler, pattern='^cancel_edit'),
            CommandHandler('cancel', cancel_edit_command)
        ],
    )

async def handle_transaction_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает начало диалога добавления транзакции"""
    text = update.message.text
    if text == '💸 Добавить расход':
        return await add_expense(update, context)
    elif text == '💳 Добавить доход':
        return await add_income(update, context)