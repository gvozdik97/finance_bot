# finance_bot/bot/bot.py

import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from .handlers import start, show_stats, export_data, show_help, handle_menu_commands
from .conversations import (
    create_transaction_conversation_handler,
    create_budget_conversation_handler,
    create_edit_budget_conversation_handler,
    quick_input
)
from .reports_handlers import report_handler
from .budgets_handlers import (
    budget_handler, 
    delete_budget_handler, 
    overwrite_budget_handler,
    budget_category_handler
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def setup_bot():
    """Настраивает и возвращает бота"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    
    # Conversation Handlers
    application.add_handler(create_transaction_conversation_handler())
    application.add_handler(create_budget_conversation_handler())
    application.add_handler(create_edit_budget_conversation_handler())
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(report_handler, pattern='^report_'))
    application.add_handler(CallbackQueryHandler(budget_handler, pattern='^budget_'))
    application.add_handler(CallbackQueryHandler(delete_budget_handler, pattern='^(delete_budget_|cancel_delete)'))
    application.add_handler(CallbackQueryHandler(overwrite_budget_handler, pattern='^(overwrite_budget_|cancel_overwrite)'))
    
    # Обработчик текстовых сообщений (главное меню и быстрый ввод)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_commands))
    
    return application

def run_bot():
    """Запускает бота"""
    application = setup_bot()
    print("Бот запущен...")
    application.run_polling()