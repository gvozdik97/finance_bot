# bot/bot.py - ОБНОВЛЕННАЯ НАСТРОЙКА

import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .handlers import (
    start, 
    handle_menu_commands
)
from .analytics_handlers import handle_analytics_commands  # ← ОБНОВЛЕННЫЙ ИМПОРТ
from .conversations import create_transaction_conversation_handler
from .debt_conversations import create_debt_conversation_handler
from .debt_handlers import create_debt_payment_conversation_handler
from .debt_menu_handlers import handle_debt_menu_commands

logger = logging.getLogger(__name__)

def setup_bot():
    """Настраивает бота с оптимизированной аналитикой"""
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
    
    # 3. Обработчик меню аналитики (обновленный)
    analytics_commands_pattern = r'^(📊 Финансовый обзор|📈 Анализ расходов|💰 Динамика доходов|📉 Графики и отчеты|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(analytics_commands_pattern), 
        handle_analytics_commands  # ← ОБНОВЛЕННЫЙ ОБРАБОТЧИК
    ))
    
    # 4. Обработчик меню долгов
    debt_commands_pattern = r'^(📜 Мои долги|➕ Добавить долг|💳 Погасить долг|📋 План погашения|📈 Прогресс свободы|🎯 Вехи освобождения|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(debt_commands_pattern), 
        handle_debt_menu_commands
    ))
    
    # 5. Обработчик быстрого ввода долгов
    application.add_handler(MessageHandler(
        filters.Regex(r'^долг .*'), 
        handle_debt_menu_commands
    ))
    
    # 6. Обработчик главного меню (самый общий - ПОСЛЕДНИЙ)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_commands))
    
    logger.info("✅ Бот настроен с оптимизированной аналитикой")
    return application

def run_bot():
    """Запускает бота с улучшенной аналитикой"""
    try:
        application = setup_bot()
        print("🏛️ Вавилонский финансовый бот запущен")
        print("📈 Оптимизированная аналитика АКТИВИРОВАНА")
        print("🎯 Новые возможности:")
        print("   • 📊 Финансовый обзор")
        print("   • 📈 Анализ расходов по категориям") 
        print("   • 💰 Динамика доходов")
        print("   • 📉 Практичные графики")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        print(f"❌ Ошибка: {e}")