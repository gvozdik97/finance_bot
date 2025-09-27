# bot/bot.py

import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .handlers import (
    start, 
    handle_menu_commands, 
    handle_analytics_commands,
    handle_visualizations_commands
)
from .conversations import create_transaction_conversation_handler
from .debt_conversations import create_debt_conversation_handler
from .debt_handlers import create_debt_payment_conversation_handler
from .debt_menu_handlers import handle_debt_menu_commands

logger = logging.getLogger(__name__)

def setup_bot():
    """Настраивает бота с полной интеграцией аналитики Фазы 3"""
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
    
    # 3. Обработчик меню визуализаций (самые специфичные команды)
    visualizations_commands_pattern = r'^(🏔️ Пирамида стабильности|🏛️ Храм богатства|🌊 Реки удачи|✨ Финансовый гороскоп|📜 Месячная летопись|🔙 Назад к аналитике|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(visualizations_commands_pattern), 
        handle_visualizations_commands
    ))
    
    # 4. Обработчик меню аналитики (специфичные команды)
    analytics_commands_pattern = r'^(🏛️ Финансовое здоровье|🔮 Прогноз накоплений|📊 Анализ расходов|📈 Тренды доходов|🎯 Паттерны расходов|🎨 Визуализации|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(analytics_commands_pattern), 
        handle_analytics_commands
    ))
    
    # 5. Обработчик меню долгов (специфичные команды)
    debt_commands_pattern = r'^(📜 Мои долги|➕ Добавить долг|💳 Погасить долг|📋 План погашения|📈 Прогресс свободы|🎯 Вехи освобождения|📊 Статистика долгов|🏠 Главное меню)$'
    application.add_handler(MessageHandler(
        filters.Regex(debt_commands_pattern), 
        handle_debt_menu_commands
    ))
    
    # 6. Обработчик быстрого ввода долгов
    application.add_handler(MessageHandler(
        filters.Regex(r'^долг .*'), 
        handle_debt_menu_commands
    ))
    
    # 7. Обработчик главного меню (самый общий - ПОСЛЕДНИЙ)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_commands))
    
    logger.info("✅ Бот настроен с полной интеграцией аналитики Фазы 3")
    return application

def run_bot():
    """Запускает бота с расширенной аналитикой"""
    try:
        application = setup_bot()
        print("🏛️ Вавилонский финансовый бот запущен")
        print("📈 Фаза 3: Расширенная аналитика АКТИВИРОВАНА")
        print("🎨 Новые возможности:")
        print("   • Анализ трендов доходов")
        print("   • Паттерны расходов") 
        print("   • Вавилонские визуализации")
        print("   • Финансовые прогнозы")
        print("   • Месячные отчеты")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        print(f"❌ Ошибка: {e}")