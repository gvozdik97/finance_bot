# finance_bot/bot/common.py

from keyboards.main_menu import get_main_menu_keyboard

async def show_main_menu(update, context):
    """Показывает главное меню"""
    await update.message.reply_text("Выберите действие:", reply_markup=get_main_menu_keyboard())

async def show_main_menu_from_query(query, context):
    """Показывает главное меню из callback query"""
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )