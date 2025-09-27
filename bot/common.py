# bot/common.py - УПРОЩЕННАЯ ВЕРСИЯ

from keyboards.main_menu import get_main_menu_keyboard
from services.babylon_service import babylon_service

async def show_main_menu(update, context):
    """Показывает главное меню с вавилонской мудростью"""
    quote = babylon_service.get_daily_quote()
    message = f"💡 *Мудрость Вавилона:* {quote}\n\nВыберите действие:"
    
    await update.message.reply_text(
        message, 
        parse_mode='Markdown', 
        reply_markup=get_main_menu_keyboard()
    )

async def show_main_menu_from_query(query, context):
    """Показывает главное меню из callback query"""
    quote = babylon_service.get_daily_quote()
    message = f"💡 *Мудрость Вавилона:* {quote}\n\nВыберите действие:"
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=message,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )