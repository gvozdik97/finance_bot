# bot/transactions_handlers.py
import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.transaction_service import transaction_service
from keyboards.transactions_menu import get_transactions_menu_keyboard
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def handle_transactions_menu_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды меню транзакций"""
    text = update.message.text
    
    if text == '💳 Добавить доход':
        from .conversations import add_income
        return await add_income(update, context)
    elif text == '💸 Добавить расход':
        from .conversations import add_expense
        return await add_expense(update, context)
    elif text == '📋 История операций':
        await show_transaction_history(update, context)
    elif text == '✏️ Редактировать':
        from .transaction_editor_handlers import show_edit_menu  # ← ИЗМЕНЕНИЕ
        await show_edit_menu(update, context)
    elif text == '🏠 Главное меню':
        from .common import show_main_menu
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "❌ Команда не распознана",
            reply_markup=get_transactions_menu_keyboard()
        )

async def show_transactions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню управления транзакциями"""
    menu_text = """
💼 *УПРАВЛЕНИЕ ТРАНЗАКЦИЯМИ*

Выберите действие:
• 💳 Добавить доход - пополнение бюджета
• 💸 Добавить расход - списание средств  
• 📋 История операций - последние транзакции
• ✏️ Редактировать - исправить ошибку

💡 Все изменения сразу отражаются на балансах
"""
    await update.message.reply_text(
        menu_text,
        parse_mode='Markdown',
        reply_markup=get_transactions_menu_keyboard()
    )

async def show_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает историю последних транзакций"""
    user_id = update.message.from_user.id
    
    try:
        transactions = transaction_service.get_transaction_history(user_id, limit=10)
        
        history_text = "📋 *ПОСЛЕДНИЕ ОПЕРАЦИИ*\n\n"
        
        if not transactions:
            history_text += "📭 Операций пока нет\n💡 Добавьте первую транзакцию!"
        else:
            for i, trans in enumerate(transactions, 1):
                emoji = "💳" if trans[0] == 'income' else "💸"
                sign = "+" if trans[0] == 'income' else "-"
                history_text += f"{i}. {emoji} {trans[2]}: {sign}{trans[1]:,.0f} руб.\n"
                history_text += f"   📝 {trans[3]}\n"
                history_text += f"   📅 {trans[4][:16]}\n\n"
        
        await update.message.reply_text(
            history_text,
            parse_mode='Markdown',
            reply_markup=get_transactions_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Transaction history error: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении истории операций",
            reply_markup=get_transactions_menu_keyboard()
        )

async def start_edit_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс редактирования транзакции"""
    # Временная заглушка - функция будет реализована в Фазе 3
    await update.message.reply_text(
        "✏️ *Редактирование транзакций*\n\n"
        "🔧 Функция находится в разработке\n"
        "Скоро вы сможете исправлять свои транзакции!\n\n"
        "💡 Пока используйте раздел 📋 История операций для просмотра",
        parse_mode='Markdown',
        reply_markup=get_transactions_menu_keyboard()
    )