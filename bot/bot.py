# bot/bot.py - ФИНАЛЬНАЯ ВЕРСИЯ
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .handlers import start, handle_menu_commands
from .analytics_handlers import handle_analytics_commands
from .conversations import create_transaction_conversation_handler
from .debt_conversations import create_debt_conversation_handler
from .debt_handlers import create_debt_payment_conversation_handler
from .debt_menu_handlers import handle_debt_menu_commands
from .budget_handlers import create_budget_conversation_handler, handle_budget_menu_commands
from .settings_handlers import create_settings_conversation_handler, handle_settings_menu_commands
from .transaction_editor_handlers import create_edit_conversation_handler, handle_edit_menu_commands
from .transactions_handlers import handle_transactions_menu_commands

logger = logging.getLogger(__name__)

def setup_bot():
    """Настраивает бота с полным функционалом"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 📍 ВАЖНО: Порядок обработчиков от специфичных к общим
    
    # 1. Команда /start (самая специфичная)
    application.add_handler(CommandHandler("start", start))
    
    # 2. Conversation Handlers (очень специфичные)
    application.add_handler(create_transaction_conversation_handler())
    application.add_handler(create_debt_conversation_handler())
    application.add_handler(create_debt_payment_conversation_handler())
    application.add_handler(create_budget_conversation_handler())
    application.add_handler(create_settings_conversation_handler())
    application.add_handler(create_edit_conversation_handler())
    
    # 3. Обработчик меню транзакций
    transactions_commands_pattern = r'^(💳 Добавить доход|💸 Добавить расход|📋 История операций|✏️ Редактировать|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(transactions_commands_pattern), 
        handle_transactions_menu_commands
    ))
    
    # 4. Обработчик меню бюджетирования
    budget_commands_pattern = r'^(💰 Мои бюджеты|🎯 Установить бюджет|💡 Рекомендации|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(budget_commands_pattern), 
        handle_budget_menu_commands
    ))
    
    # 5. Обработчик меню настроек
    settings_commands_pattern = r'^(⚙️ Настройки накоплений|📊 Текущие настройки|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(settings_commands_pattern), 
        handle_settings_menu_commands
    ))
    
    # 6. Обработчик меню редактирования
    edit_commands_pattern = r'^(✏️ Выбрать транзакцию|🗑️ Удалить транзакцию|📋 Список транзакций|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(edit_commands_pattern), 
        handle_edit_menu_commands
    ))
    
    # 7. Обработчик меню аналитики
    analytics_commands_pattern = r'^(📊 Финансовый обзор|📈 Анализ расходов|💰 Динамика доходов|📉 Графики и отчеты|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(analytics_commands_pattern), 
        handle_analytics_commands
    ))
    
    # 8. Обработчик меню долгов
    debt_commands_pattern = r'^(📜 Мои долги|➕ Добавить долг|💳 Погасить долг|📋 План погашения|📈 Прогресс свободы|🎯 Вехи освобождения|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(debt_commands_pattern), 
        handle_debt_menu_commands
    ))
    
    # 9. Обработчик быстрого ввода долгов
    application.add_handler(MessageHandler(
        filters.Regex(r'^долг .*'), 
        handle_debt_menu_commands
    ))
    
    # 10. Обработчик главного меню (самый общий - ПОСЛЕДНИЙ)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_commands))
    
    logger.info("✅ Бот настроен с полным функционалом")
    return application

def run_bot():
    """Запускает бота с полным функционалом"""
    try:
        application = setup_bot()
        print("🏛️ Вавилонский финансовый бот запущен")
        print("🎉 НОВЫЙ ФУНКЦИОНАЛ АКТИВИРОВАН:")
        print("   • 💼 Упрощенное меню транзакций")
        print("   • ⚙️ Гибкое правило накоплений (0-100%)")
        print("   • ✏️ Редактирование транзакций")
        print("   • 💰 Система бюджетирования")
        print("   • 🎯 Умные рекомендации")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        print(f"❌ Ошибка: {e}")