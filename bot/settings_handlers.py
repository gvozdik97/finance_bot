# bot/settings_handlers.py
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from services.user_settings_service import user_settings_service
from services.wallet_service import wallet_service
from keyboards.settings_menu import get_settings_menu_keyboard, get_savings_options_keyboard
from keyboards.main_menu import get_main_menu_keyboard, remove_keyboard
from .common import show_main_menu

logger = logging.getLogger(__name__)

# Состояния для диалога настроек
SETTINGS_OPTION, SAVINGS_PERCENT = range(20, 22)

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню настроек"""
    user_id = update.message.from_user.id
    settings = user_settings_service.get_user_settings(user_id)
    
    if not settings:
        user_settings_service.init_user_settings(user_id)
        settings = user_settings_service.get_user_settings(user_id)
    
    current_status = "включены" if settings.auto_savings else "выключены"
    current_percent = settings.savings_rate
    
    menu_text = f"""
⚙️ *НАСТРОЙКИ НАКОПЛЕНИЙ*

Текущие настройки:
• 📊 Автонакопления: {current_status}
• 💰 Процент накоплений: {current_percent}%

Выберите действие:
• ⚙️ Настройки накоплений - изменить стратегию
• 📊 Текущие настройки - просмотр параметров

💡 *Совет:* Начните с 10% и увеличивайте постепенно
"""
    await update.message.reply_text(
        menu_text,
        parse_mode='Markdown',
        reply_markup=get_settings_menu_keyboard()
    )

async def show_current_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текущие настройки пользователя"""
    user_id = update.message.from_user.id
    settings = user_settings_service.get_user_settings(user_id)
    
    if not settings:
        user_settings_service.init_user_settings(user_id)
        settings = user_settings_service.get_user_settings(user_id)
    
    auto_savings_emoji = "✅" if settings.auto_savings else "❌"
    auto_savings_text = "включены" if settings.auto_savings else "выключены"
    
    settings_text = f"""
📊 *ВАШИ ТЕКУЩИЕ НАСТРОЙКИ*

{auto_savings_emoji} *Автонакопления:* {auto_savings_text}
💰 *Процент накоплений:* {settings.savings_rate}%

💡 *Как это работает:*
• При добавлении дохода {settings.savings_rate}% идет в Золотой запас
• Остальные {100-settings.savings_rate}% поступают в Бюджет на жизнь
• Накопления защищены от случайных трат

🎯 *Рекомендация:* Стремитесь к 10-20% накоплений
"""
    await update.message.reply_text(
        settings_text,
        parse_mode='Markdown',
        reply_markup=get_settings_menu_keyboard()
    )

async def start_savings_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс настройки накоплений"""
    await update.message.reply_text(
        "💰 *НАСТРОЙКА СТРАТЕГИИ НАКОПЛЕНИЙ*\n\n"
        "Выберите предпочтительную стратегию:\n\n"
        "• 💰 Классические 10% - правило из Вавилона\n"
        "• 💸 Без накоплений - весь доход в бюджет\n"
        "• 🎯 Настроить процент - свой процент\n",
        parse_mode='Markdown',
        reply_markup=get_savings_options_keyboard()
    )
    return SETTINGS_OPTION

async def handle_savings_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор стратегии накоплений"""
    option = update.message.text
    user_id = update.message.from_user.id
    
    if option == '🏠 Главное меню':
        await show_main_menu(update, context)
        return ConversationHandler.END
    
    if option == '💰 Классические 10%':
        success = user_settings_service.update_savings_rate(user_id, 10.0)
        success &= user_settings_service.toggle_auto_savings(user_id, True)
        
        if success:
            await update.message.reply_text(
                "✅ *Стратегия установлена: Классические 10%*\n\n"
                "💎 Теперь 10% от каждого дохода будет автоматически "
                "откладываться в Золотой запас!\n\n"
                "🏛️ *Мудрость Вавилона:* «Часть того, что ты зарабатываешь, должна остаться у тебя»",
                parse_mode='Markdown',
                reply_markup=get_settings_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при сохранении настроек",
                reply_markup=get_settings_menu_keyboard()
            )
        
        return ConversationHandler.END
    
    elif option == '💸 Без накоплений':
        success = user_settings_service.toggle_auto_savings(user_id, False)
        
        if success:
            await update.message.reply_text(
                "✅ *Накопления отключены*\n\n"
                "💡 Теперь весь доход будет поступать в Бюджет на жизнь.\n\n"
                "⚠️ *Рекомендация:* Рассмотрите возможность ручного откладывания "
                "средств для создания финансовой подушки",
                parse_mode='Markdown',
                reply_markup=get_settings_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при сохранении настроек",
                reply_markup=get_settings_menu_keyboard()
            )
        
        return ConversationHandler.END
    
    elif option == '🎯 Настроить процент':
        await update.message.reply_text(
            "🎯 *НАСТРОЙКА ПРОЦЕНТА НАКОПЛЕНИЙ*\n\n"
            "Введите желаемый процент накоплений (0-100):\n\n"
            "Пример: `15` для 15% или `25` для 25%\n"
            "💡 Рекомендуется: 10-20%",
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return SAVINGS_PERCENT
    
    else:
        await update.message.reply_text(
            "❌ Пожалуйста, выберите вариант из меню",
            reply_markup=get_savings_options_keyboard()
        )
        return SETTINGS_OPTION

async def handle_savings_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод процента накоплений"""
    try:
        percent = float(update.message.text.replace(',', '.'))
        
        if not (0 <= percent <= 100):
            await update.message.reply_text(
                "❌ Процент должен быть от 0 до 100. Введите еще раз:"
            )
            return SAVINGS_PERCENT
        
        user_id = update.message.from_user.id
        success = user_settings_service.update_savings_rate(user_id, percent)
        success &= user_settings_service.toggle_auto_savings(user_id, True)
        
        if success:
            await update.message.reply_text(
                f"✅ *Процент накоплений установлен: {percent}%*\n\n"
                f"💎 Теперь {percent}% от каждого дохода будет автоматически "
                f"откладываться в Золотой запас!\n\n"
                f"📊 Остальные {100-percent}% будут поступать в Бюджет на жизнь",
                parse_mode='Markdown',
                reply_markup=get_settings_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при сохранении настроек",
                reply_markup=get_settings_menu_keyboard()
            )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введите число. Пример: `15` для 15%"
        )
        return SAVINGS_PERCENT

async def handle_settings_menu_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды меню настроек"""
    text = update.message.text
    
    if text == '⚙️ Настройки накоплений':
        return await start_savings_settings(update, context)
    elif text == '📊 Текущие настройки':
        await show_current_settings(update, context)
    elif text == '🏠 Главное меню':
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "❌ Команда не распознана",
            reply_markup=get_settings_menu_keyboard()
        )

async def cancel_settings_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет диалог настройки"""
    await update.message.reply_text(
        "❌ Настройка отменена.",
        reply_markup=get_settings_menu_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

def create_settings_conversation_handler():
    """Создает обработчик диалога настройки"""
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^⚙️ Настройки накоплений$'), start_savings_settings)
        ],
        states={
            SETTINGS_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_savings_option)],
            SAVINGS_PERCENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_savings_percent)]
        },
        fallbacks=[CommandHandler('cancel', cancel_settings_conversation)],
        allow_reentry=True
    )