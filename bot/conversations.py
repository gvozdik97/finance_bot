# bot/conversations.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from utils.constants import AMOUNT, CATEGORY, DESCRIPTION
from utils.validators import validate_amount
from utils.categorizers import clean_category_name, categorize_expense, categorize_income

from services.transaction_service import transaction_service
from services.simple_budget_service import simple_budget_service
from services.babylon_service import babylon_service
from services.wallet_service import wallet_service  # ✅ ДОБАВИЛИ ИМПОРТ

from keyboards.main_menu import get_main_menu_keyboard, get_category_keyboard, remove_keyboard

from .common import show_main_menu

logger = logging.getLogger(__name__)

# ============================================================================
# ЧИСТАЯ ВАВИЛОНСКАЯ ЛОГИКА ТРАНЗАКЦИЙ - ИСПРАВЛЕННАЯ
# ============================================================================

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Чистое вавилонское добавление дохода"""
    await update.message.reply_text(
        "💳 *Добавление дохода*\n\n"
        "🏛️ *По правилам Вавилона:*\n"
        "• 10% → 💰 Золотой запас (накопления)\n"  
        "• 90% → 💼 Бюджет на жизнь (расходы)\n\n"
        "Введите сумму дохода:",
        parse_mode='Markdown', 
        reply_markup=remove_keyboard()
    )
    context.user_data['type'] = 'income'
    return AMOUNT

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Чистое вавилонское добавление расхода - ИСПРАВЛЕНО"""
    user_id = update.message.from_user.id
    living_budget = wallet_service.get_wallet_balance(user_id, 'living_budget')  # ✅ ИСПРАВИЛИ
    
    await update.message.reply_text(
        f"💸 *Добавление расхода*\n\n"
        f"💼 *Доступно в Бюджете на жизнь:* {living_budget:,.0f} руб.\n\n"
        f"Введите сумму расхода:",
        parse_mode='Markdown',
        reply_markup=remove_keyboard()
    )
    context.user_data['type'] = 'expense'
    return AMOUNT

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод суммы с чистой вавилонской логикой - ИСПРАВЛЕНО"""
    is_valid, result = validate_amount(update.message.text)
    
    if not is_valid:
        await update.message.reply_text(result)
        return AMOUNT
    
    amount = result
    user_id = update.message.from_user.id
    context.user_data['amount'] = amount
    
    # ВАВИЛОНСКАЯ ПРОВЕРКА: расходы только из 90%
    if context.user_data['type'] == 'expense':
        affordability = wallet_service.can_afford_expense(user_id, amount)  # ✅ ИСПРАВИЛИ
        
        if not affordability['can_afford']:
            await update.message.reply_text(
                f"🚫 *Недостаточно средств в Бюджете на жизнь!*\n\n"
                f"💼 Доступно: {affordability['available']:,.0f} руб.\n"
                f"💸 Нужно: {affordability['needed']:,.0f} руб.\n"
                f"📉 Не хватает: {affordability['shortfall']:,.0f} руб.\n\n"
                f"💡 *Мудрость Вавилона:* \"Контролируй расходы в рамках 90%\"",
                parse_mode='Markdown'
            )
            await show_main_menu(update, context)
            context.user_data.clear()
            return ConversationHandler.END
    
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
    """Сохраняет транзакцию с чистой вавилонской логикой"""
    user_data = context.user_data
    
    if description is None:
        description = update.message.text if update.message and update.message.text != '/skip' else "Без описания"
    
    user_id = update.message.from_user.id
    amount = user_data['amount']
    category = user_data['category']
    transaction_type = user_data['type']
    
    try:
        if transaction_type == 'income':
            # ЧИСТОЕ ВАВИЛОНСКОЕ РАСПРЕДЕЛЕНИЕ
            result = transaction_service.add_income(user_id, amount, category, description)
            
            if result['success']:
                # Обновляем прогресс правила 10%
                babylon_service.update_rule_progress(user_id, '10_percent_rule', 100.0)
                
                await update.message.reply_text(result['message'], parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ {result['error']}")
                
        else:  # expense
            # ЧИСТАЯ ВАВИЛОНСКАЯ ПРОВЕРКА
            result = transaction_service.add_expense(user_id, amount, category, description)
            
            if result['success']:
                # Обновляем прогресс контроля расходов
                await update_expense_progress(user_id)
                
                # Проверка бюджетного лимита
                await check_budget_limit(update, user_id, category, amount)
                
                await update.message.reply_text(result['message'], parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ {result['error']}")
        
    except Exception as e:
        logger.error(f"Transaction save error: {e}")
        await update.message.reply_text("❌ Ошибка при сохранении транзакции.")
    
    # Возврат в главное меню
    await show_main_menu(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def update_expense_progress(user_id: int):
    """Обновляет прогресс контроля расходов"""
    living_budget = wallet_service.get_wallet_balance(user_id, 'living_budget')  # ✅ ИСПРАВИЛИ
    gold_reserve = wallet_service.get_wallet_balance(user_id, 'gold_reserve')    # ✅ ИСПРАВИЛИ
    total_balance = living_budget + gold_reserve
    
    if total_balance > 0:
        # Идеал: living_budget составляет 90% от общего баланса
        ideal_ratio = 90.0
        current_ratio = (living_budget / total_balance * 100) if total_balance > 0 else 0
        progress = min(100.0, (current_ratio / ideal_ratio * 100))
        
        babylon_service.update_rule_progress(user_id, 'control_expenses', progress)

async def check_budget_limit(update: Update, user_id: int, category: str, amount: float):
    """Проверяет лимит категории с вавилонским акцентом"""
    budget_check = simple_budget_service.check_spending(user_id, category, amount)
    
    if budget_check.get('has_limit') and budget_check['exceeded']:
        await update.message.reply_text(
            f"⚠️ *Превышение бюджетного лимита!*\n\n"
            f"Категория: {category}\n"
            f"Лимит в месяц: {budget_check['monthly_limit']:,.0f} руб.\n"
            f"Уже потрачено: {budget_check['current_spent']:,.0f} руб.\n"
            f"После траты: {budget_check['total_after_expense']:,.0f} руб.\n"
            f"📛 Превышение: {budget_check['overspend']:,.0f} руб.\n\n"
            f"💡 *Совет Вавилона:* \"Мудрый человек знает меру в расходах\"",
            parse_mode='Markdown'
        )

# ============================================================================
# БЫСТРЫЙ ВВОД - ЧИСТАЯ ВАВИЛОНСКАЯ ЛОГИКА
# ============================================================================

async def quick_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрый ввод с чистой вавилонской логикой"""
    text = update.message.text.strip()
    words = text.split()
    
    if len(words) < 2:
        await update.message.reply_text(
            "❌ *Формат быстрого ввода:*\n"
            "`1500 еда обед` - расход\n" 
            "`-50000 зарплата` - доход",
            parse_mode='Markdown'
        )
        return
    
    try:
        amount = float(words[0])
        category_word = words[1].lower()
        description = ' '.join(words[2:]) if len(words) > 2 else "Быстрый ввод"
        
        user_id = update.message.from_user.id
        
        if amount < 0:  # Отрицательная сумма = доход
            amount = abs(amount)
            category = categorize_income(category_word)
            result = transaction_service.add_income(user_id, amount, category, description)
            
            if result['success']:
                babylon_service.update_rule_progress(user_id, '10_percent_rule', 100.0)
                message = result['message']
            else:
                message = f"❌ {result['error']}"
                
        else:  # Положительная сумма = расход
            category = categorize_expense(category_word)
            
            # ✅ ДОБАВИЛИ ПРОВЕРКУ ДОСТУПНОСТИ СРЕДСТВ
            affordability = wallet_service.can_afford_expense(user_id, amount)
            if not affordability['can_afford']:
                await update.message.reply_text(
                    f"🚫 *Недостаточно средств в Бюджете на жизнь!*\n"
                    f"Доступно: {affordability['available']:,.0f} руб.\n"
                    f"Нужно: {affordability['needed']:,.0f} руб.",
                    parse_mode='Markdown'
                )
                return
            
            result = transaction_service.add_expense(user_id, amount, category, description)
            
            if result['success']:
                await update_expense_progress(user_id)
                budget_check = simple_budget_service.check_spending(user_id, category, amount)
                
                if budget_check.get('has_limit') and budget_check['exceeded']:
                    message = f"{result['message']}\n\n⚠️ *Превышен бюджет категории!*"
                else:
                    message = result['message']
            else:
                message = f"❌ {result['error']}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text(
            "❌ *Ошибка формата!*\n"
            "Примеры:\n"
            "• `10000 зарплата` - доход 10000 руб.\n"
            "• `1500 еда обед` - расход 1500 руб. на еду",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Quick input error: {e}")
        await update.message.reply_text("❌ Ошибка при быстром вводе.")

# ============================================================================
# CONVERSATION HANDLERS - УПРОЩЕННЫЕ
# ============================================================================

def create_transaction_conversation_handler():
    """Создает упрощенный обработчик диалогов"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(💳 Добавить доход|💸 Добавить расход)$'), 
                          handle_transaction_start)
        ],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_handler)],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_transaction),
                CommandHandler('skip', skip_description)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
        allow_reentry=True
    )

# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

async def handle_transaction_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает начало диалога добавления транзакции"""
    text = update.message.text
    if text == '💸 Добавить расход':
        return await add_expense(update, context)
    elif text == '💳 Добавить доход':
        return await add_income(update, context)

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет текущий диалог"""
    await update.message.reply_text(
        "❌ Операция отменена.",
        reply_markup=get_main_menu_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

# Экспорт функций
__all__ = [
    'add_income', 'add_expense', 'amount_handler', 'category_handler', 
    'save_transaction', 'quick_input', 'create_transaction_conversation_handler'
]