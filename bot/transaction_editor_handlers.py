# bot/transaction_editor_handlers.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from services.transaction_editor import transaction_editor
from services.transaction_service import transaction_service
from keyboards.settings_menu import get_edit_transactions_keyboard, get_edit_confirmation_keyboard
from keyboards.main_menu import get_main_menu_keyboard, remove_keyboard
from keyboards.transactions_menu import get_transactions_menu_keyboard
from .common import show_main_menu

logger = logging.getLogger(__name__)

# Состояния для диалога редактирования
EDIT_SELECT_TRANSACTION, EDIT_CHOOSE_FIELD, EDIT_AMOUNT, EDIT_CATEGORY, EDIT_DESCRIPTION, EDIT_CONFIRM, DELETE_SELECT, DELETE_CONFIRM = range(30, 38)

def _format_transaction_date(date_value):
    """Форматирует дату транзакции, обрабатывая разные типы данных"""
    try:
        if isinstance(date_value, str):
            # Если дата в строковом формате, пытаемся распарсить
            if 'T' in date_value:
                # Формат ISO: '2024-01-15T10:30:00'
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            elif ' ' in date_value:
                # Формат SQLite: '2024-01-15 10:30:00'
                date_obj = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
            else:
                # Другие форматы
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
        elif isinstance(date_value, datetime):
            # Если уже объект datetime
            date_obj = date_value
        else:
            # Если непонятный формат, используем текущее время
            date_obj = datetime.now()
        
        return date_obj.strftime('%d.%m %H:%M')
        
    except Exception as e:
        logger.error(f"Error formatting date {date_value}: {e}")
        return "дата неизвестна"

async def show_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню редактирования транзакций"""
    menu_text = """
✏️ *РЕДАКТИРОВАНИЕ ТРАНЗАКЦИЙ*

Исправляйте ошибки и управляйте историей:

• ✏️ Выбрать транзакцию - изменить сумму или категорию
• 🗑️ Удалить транзакцию - полностью удалить операцию
• 📋 Список транзакций - просмотр для выбора

💡 *Важно:* Все изменения автоматически пересчитывают балансы
"""
    await update.message.reply_text(
        menu_text,
        parse_mode='Markdown',
        reply_markup=get_edit_transactions_keyboard()
    )

async def start_edit_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс редактирования транзакции"""
    user_id = update.message.from_user.id
    transactions = transaction_editor.get_recent_transactions_for_edit(user_id, limit=5)
    
    if not transactions:
        await update.message.reply_text(
            "📭 *Нет транзакций для редактирования*\n\n"
            "Добавьте несколько операций, чтобы они появились здесь.",
            parse_mode='Markdown',
            reply_markup=get_edit_transactions_keyboard()
        )
        return ConversationHandler.END
    
    # Сохраняем транзакции в контексте
    context.user_data['edit_transactions'] = transactions
    
    transactions_text = "📋 *ВЫБЕРИТЕ ТРАНЗАКЦИЮ ДЛЯ РЕДАКТИРОВАНИЯ*\n\n"
    
    for i, transaction in enumerate(transactions, 1):
        emoji = "💳" if transaction.type == 'income' else "💸"
        sign = "+" if transaction.type == 'income' else "-"
        
        # Исправляем форматирование даты
        date_str = _format_transaction_date(transaction.date)
        
        transactions_text += f"{i}. {emoji} {transaction.category}: {sign}{transaction.amount:,.0f} руб.\n"
        transactions_text += f"   📝 {transaction.description}\n"
        transactions_text += f"   📅 {date_str}\n\n"
    
    transactions_text += "Введите номер транзакции:"
    
    await update.message.reply_text(
        transactions_text,
        parse_mode='Markdown',
        reply_markup=remove_keyboard()
    )
    return EDIT_SELECT_TRANSACTION

async def handle_transaction_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор транзакции для редактирования"""
    try:
        transaction_number = int(update.message.text)
        transactions = context.user_data.get('edit_transactions', [])
        
        if transaction_number < 1 or transaction_number > len(transactions):
            await update.message.reply_text(
                f"❌ Неверный номер. Введите число от 1 до {len(transactions)}:"
            )
            return EDIT_SELECT_TRANSACTION
        
        selected_transaction = transactions[transaction_number - 1]
        context.user_data['selected_transaction'] = selected_transaction
        context.user_data['selected_transaction_id'] = selected_transaction.id
        
        # Исправляем форматирование даты
        date_str = _format_transaction_date(selected_transaction.date)
        
        # Показываем опции редактирования
        await update.message.reply_text(
            f"✏️ *РЕДАКТИРОВАНИЕ ТРАНЗАКЦИИ*\n\n"
            f"📊 Транзакция #{transaction_number}:\n"
            f"• Тип: {'доход' if selected_transaction.type == 'income' else 'расход'}\n"
            f"• Сумма: {selected_transaction.amount:,.0f} руб.\n"
            f"• Категория: {selected_transaction.category}\n"
            f"• Описание: {selected_transaction.description}\n"
            f"• Дата: {date_str}\n\n"
            f"Что вы хотите изменить?\n"
            f"Введите: `сумма`, `категория` или `описание`",
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return EDIT_CHOOSE_FIELD
        
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введите номер транзакции:"
        )
        return EDIT_SELECT_TRANSACTION

async def handle_field_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор поля для редактирования"""
    field = update.message.text.lower().strip()
    transaction = context.user_data['selected_transaction']
    
    if field == 'сумма':
        await update.message.reply_text(
            f"💰 *ИЗМЕНЕНИЕ СУММЫ*\n\n"
            f"Текущая сумма: {transaction.amount:,.0f} руб.\n"
            f"Введите новую сумму:",
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return EDIT_AMOUNT
    
    elif field == 'категория':
        from keyboards.main_menu import get_category_keyboard
        await update.message.reply_text(
            f"🏷️ *ИЗМЕНЕНИЕ КАТЕГОРИИ*\n\n"
            f"Текущая категория: {transaction.category}\n"
            f"Выберите новую категорию:",
            parse_mode='Markdown',
            reply_markup=get_category_keyboard(transaction.type)
        )
        return EDIT_CATEGORY
    
    elif field == 'описание':
        await update.message.reply_text(
            f"📝 *ИЗМЕНЕНИЕ ОПИСАНИЯ*\n\n"
            f"Текущее описание: {transaction.description}\n"
            f"Введите новое описание:",
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return EDIT_DESCRIPTION
    
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, введите: `сумма`, `категория` или `описание`"
        )
        return EDIT_CHOOSE_FIELD

async def handle_amount_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает изменение суммы"""
    try:
        new_amount = float(update.message.text.replace(',', '.'))
        
        if new_amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной. Введите еще раз:")
            return EDIT_AMOUNT
        
        context.user_data['new_amount'] = new_amount
        transaction = context.user_data['selected_transaction']
        
        await update.message.reply_text(
            f"✅ *ПОДТВЕРЖДЕНИЕ ИЗМЕНЕНИЯ*\n\n"
            f"📊 Транзакция будет изменена:\n"
            f"• Старая сумма: {transaction.amount:,.0f} руб.\n"
            f"• Новая сумма: {new_amount:,.0f} руб.\n"
            f"• Изменение: {new_amount - transaction.amount:+,.0f} руб.\n\n"
            f"💡 Балансы будут автоматически пересчитаны\n"
            f"Подтвердить изменение?",
            parse_mode='Markdown',
            reply_markup=get_edit_confirmation_keyboard()
        )
        return EDIT_CONFIRM
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число. Пример: `5000`")
        return EDIT_AMOUNT

async def handle_category_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает изменение категории"""
    new_category = update.message.text
    from utils.categorizers import clean_category_name
    new_category = clean_category_name(new_category)
    
    context.user_data['new_category'] = new_category
    transaction = context.user_data['selected_transaction']
    
    await update.message.reply_text(
        f"✅ *ПОДТВЕРЖДЕНИЕ ИЗМЕНЕНИЯ*\n\n"
        f"📊 Транзакция будет изменена:\n"
        f"• Старая категория: {transaction.category}\n"
        f"• Новая категория: {new_category}\n\n"
        f"Подтвердить изменение?",
        parse_mode='Markdown',
        reply_markup=get_edit_confirmation_keyboard()
    )
    return EDIT_CONFIRM

async def handle_description_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает изменение описания"""
    new_description = update.message.text
    context.user_data['new_description'] = new_description
    transaction = context.user_data['selected_transaction']
    
    await update.message.reply_text(
        f"✅ *ПОДТВЕРЖДЕНИЕ ИЗМЕНЕНИЯ*\n\n"
        f"📊 Транзакция будет изменена:\n"
        f"• Старое описание: {transaction.description}\n"
        f"• Новое описание: {new_description}\n\n"
        f"Подтвердить изменение?",
        parse_mode='Markdown',
        reply_markup=get_edit_confirmation_keyboard()
    )
    return EDIT_CONFIRM

async def handle_edit_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает подтверждение редактирования"""
    response = update.message.text
    
    if response == '✅ Подтвердить':
        # Проверяем, что у нас есть необходимые данные
        if 'selected_transaction_id' not in context.user_data:
            await update.message.reply_text(
                "❌ Ошибка: транзакция не выбрана. Начните заново.",
                reply_markup=get_edit_transactions_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        user_id = update.message.from_user.id
        transaction_id = context.user_data['selected_transaction_id']
        
        # Собираем изменения
        changes = {}
        if 'new_amount' in context.user_data:
            changes['new_amount'] = context.user_data['new_amount']
        if 'new_category' in context.user_data:
            changes['new_category'] = context.user_data['new_category']
        if 'new_description' in context.user_data:
            changes['new_description'] = context.user_data['new_description']
        
        # Проверяем, что есть хотя бы одно изменение
        if not changes:
            await update.message.reply_text(
                "❌ Нет изменений для сохранения",
                reply_markup=get_edit_transactions_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        # Применяем изменения
        result = transaction_editor.edit_transaction(
            user_id, transaction_id,
            new_amount=changes.get('new_amount'),
            new_category=changes.get('new_category'),
            new_description=changes.get('new_description')
        )
        
        if result['success']:
            await update.message.reply_text(
                result['message'],
                parse_mode='Markdown',
                reply_markup=get_edit_transactions_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ {result['error']}",
                reply_markup=get_edit_transactions_keyboard()
            )
    
    else:  # Отмена или любой другой текст
        await update.message.reply_text(
            "❌ Редактирование отменено",
            reply_markup=get_edit_transactions_keyboard()
        )
    
    context.user_data.clear()
    return ConversationHandler.END

async def start_delete_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс удаления транзакции"""
    user_id = update.message.from_user.id
    transactions = transaction_editor.get_recent_transactions_for_edit(user_id, limit=5)
    
    if not transactions:
        await update.message.reply_text(
            "📭 *Нет транзакций для удаления*",
            parse_mode='Markdown',
            reply_markup=get_edit_transactions_keyboard()
        )
        return ConversationHandler.END
    
    context.user_data['delete_transactions'] = transactions
    
    transactions_text = "🗑️ *ВЫБЕРИТЕ ТРАНЗАКЦИЮ ДЛЯ УДАЛЕНИЯ*\n\n"
    
    for i, transaction in enumerate(transactions, 1):
        emoji = "💳" if transaction.type == 'income' else "💸"
        sign = "+" if transaction.type == 'income' else "-"
        
        # Исправляем форматирование даты
        date_str = _format_transaction_date(transaction.date)
        
        transactions_text += f"{i}. {emoji} {transaction.category}: {sign}{transaction.amount:,.0f} руб.\n"
        transactions_text += f"   📝 {transaction.description}\n"
        transactions_text += f"   📅 {date_str}\n\n"
    
    transactions_text += "Введите номер транзакции для удаления:"
    
    await update.message.reply_text(
        transactions_text,
        parse_mode='Markdown',
        reply_markup=remove_keyboard()
    )
    return DELETE_SELECT

async def handle_delete_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор транзакции для удаления"""
    try:
        transaction_number = int(update.message.text)
        transactions = context.user_data.get('delete_transactions', [])
        
        if transaction_number < 1 or transaction_number > len(transactions):
            await update.message.reply_text(
                f"❌ Неверный номер. Введите число от 1 до {len(transactions)}:"
            )
            return DELETE_SELECT
        
        selected_transaction = transactions[transaction_number - 1]
        
        await update.message.reply_text(
            f"⚠️ *ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ*\n\n"
            f"Вы действительно хотите удалить транзакцию?\n\n"
            f"📊 Транзакция #{transaction_number}:\n"
            f"• Тип: {'доход' if selected_transaction.type == 'income' else 'расход'}\n"
            f"• Сумма: {selected_transaction.amount:,.0f} руб.\n"
            f"• Категория: {selected_transaction.category}\n\n"
            f"💡 Балансы будут автоматически пересчитаны",
            parse_mode='Markdown',
            reply_markup=get_edit_confirmation_keyboard()
        )
        
        context.user_data['delete_transaction_id'] = selected_transaction.id
        return DELETE_CONFIRM
        
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введите номер транзакции:"
        )
        return DELETE_SELECT

async def handle_delete_execution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выполняет удаление транзакции"""
    response = update.message.text
    
    if response == '✅ Подтвердить':
        # Проверяем, что у нас есть ID транзакции для удаления
        if 'delete_transaction_id' not in context.user_data:
            await update.message.reply_text(
                "❌ Ошибка: транзакция не выбрана. Начните заново.",
                reply_markup=get_edit_transactions_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        user_id = update.message.from_user.id
        transaction_id = context.user_data['delete_transaction_id']
        
        result = transaction_editor.delete_transaction(user_id, transaction_id)
        
        if result['success']:
            await update.message.reply_text(
                result['message'],
                parse_mode='Markdown',
                reply_markup=get_edit_transactions_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ {result['error']}",
                reply_markup=get_edit_transactions_keyboard()
            )
    
    else:  # Отмена или любой другой текст
        await update.message.reply_text(
            "❌ Удаление отменено",
            reply_markup=get_edit_transactions_keyboard()
        )
    
    context.user_data.clear()
    return ConversationHandler.END

async def show_transactions_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список транзакций для выбора"""
    user_id = update.message.from_user.id
    transactions = transaction_service.get_transaction_history(user_id, limit=10)
    
    history_text = "📋 *ПОСЛЕДНИЕ ОПЕРАЦИИ*\n\n"
    
    if not transactions:
        history_text += "📭 Операций пока нет\n💡 Добавьте первую транзакцию!"
    else:
        for i, trans in enumerate(transactions, 1):
            emoji = "💳" if trans[0] == 'income' else "💸"
            sign = "+" if trans[0] == 'income' else "-"
            
            # Форматируем дату из кортежа транзакций
            date_str = _format_transaction_date(trans[4])
            
            history_text += f"{i}. {emoji} {trans[2]}: {sign}{trans[1]:,.0f} руб.\n"
            history_text += f"   📝 {trans[3]}\n"
            history_text += f"   📅 {date_str}\n\n"
    
    await update.message.reply_text(
        history_text,
        parse_mode='Markdown',
        reply_markup=get_edit_transactions_keyboard()
    )

async def handle_edit_menu_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды меню редактирования"""
    text = update.message.text
    
    if text == '✏️ Выбрать транзакцию':
        return await start_edit_transaction(update, context)
    elif text == '🗑️ Удалить транзакцию':
        return await start_delete_transaction(update, context)
    elif text == '📋 Список транзакций':
        await show_transactions_list(update, context)
    elif text == '🏠 Главное меню':
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "❌ Команда не распознана",
            reply_markup=get_edit_transactions_keyboard()
        )

async def cancel_edit_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет диалог редактирования"""
    await update.message.reply_text(
        "❌ Редактирование отменено.",
        reply_markup=get_edit_transactions_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

def create_edit_conversation_handler():
    """Создает обработчик диалога редактирования"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^✏️ Выбрать транзакцию$'), start_edit_transaction),
            MessageHandler(filters.Regex('^🗑️ Удалить транзакцию$'), start_delete_transaction)
        ],
        states={
            EDIT_SELECT_TRANSACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction_selection)],
            EDIT_CHOOSE_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_field_selection)],
            EDIT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount_edit)],
            EDIT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category_edit)],
            EDIT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description_edit)],
            EDIT_CONFIRM: [MessageHandler(filters.Regex(r'^(✅ Подтвердить|❌ Отменить)$'), handle_edit_confirmation)],
            DELETE_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_selection)],
            DELETE_CONFIRM: [MessageHandler(filters.Regex(r'^(✅ Подтвердить|❌ Отменить)$'), handle_delete_execution)]
        },
        fallbacks=[CommandHandler('cancel', cancel_edit_conversation)],
        allow_reentry=True
    )