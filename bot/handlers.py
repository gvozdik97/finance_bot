# bot/handlers.py - ОБНОВЛЕННЫЕ ОБРАБОТЧИКИ

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.wallet_service import wallet_service
from services.babylon_service import babylon_service
from services.transaction_service import transaction_service
from services.debt_service import debt_service

from keyboards.main_menu import get_main_menu_keyboard
from keyboards.analytics_menu import get_analytics_menu_keyboard
from .common import show_main_menu
from .analytics_handlers import show_analytics_menu, handle_analytics_commands
from .conversations import add_income, add_expense, quick_input

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Чистое вавилонское приветствие"""
    user = update.message.from_user
    
    wallet_service.init_user_wallets(user.id)
    babylon_service.init_user_rules(user.id)
    
    welcome_text = babylon_service.get_welcome_message()
    
    await update.message.reply_text(
        welcome_text, 
        parse_mode='Markdown', 
        reply_markup=get_main_menu_keyboard()
    )

async def show_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает вавилонские кошельки"""
    user_id = update.message.from_user.id
    
    try:
        wallets = wallet_service.get_all_wallets(user_id)
        
        wallets_text = "🏦 *Ваши Вавилонские Кошельки*\n\n"
        
        for wallet_type, balance in wallets.items():
            display_name = wallet_service.get_wallet_display_name(wallet_type)
            wallets_text += f"{display_name}: *{balance:,.0f} руб.*\n"
        
        if wallets['gold_reserve'] > 0:
            wallets_text += f"\n💡 *Совет Вавилона:* \"Твой Золотой запас растет! Помни правило 10%\""
        else:
            wallets_text += f"\n💡 *Совет Вавилона:* \"Начни с малого - отложи 10% от следующего дохода\""
        
        await update.message.reply_text(wallets_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Wallets error: {e}")
        await update.message.reply_text("❌ Ошибка при получении кошельков.")

async def show_babylon_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает прогресс по правилам Вавилона"""
    user_id = update.message.from_user.id
    
    try:
        progress = babylon_service.get_user_progress(user_id)
        rules_info = babylon_service.rules
        
        rules_text = "🏛️ *7 Правил Богатства из Вавилона*\n\n"
        
        for rule_name, rule_data in rules_info.items():
            current_progress = progress.get(rule_name, 0)
            progress_bar = _create_progress_bar(current_progress)
            
            rules_text += f"{rule_data['emoji']} *{rule_data['name']}*\n"
            rules_text += f"{rule_data['description']}\n"
            rules_text += f"Прогресс: {progress_bar} {current_progress:.0f}%\n\n"
        
        total_progress = sum(progress.values()) / len(progress) if progress else 0
        rules_text += f"📊 *Общий прогресс:* {total_progress:.0f}%"
        
        quote = babylon_service.get_daily_quote()
        rules_text += f"\n\n💡 {quote}"
        
        await update.message.reply_text(rules_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Rules error: {e}")
        await update.message.reply_text("❌ Ошибка при получении прогресса правил.")

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простая помощь по вавилонскому боту"""
    help_text = """
ℹ️ *Помощь по Вавилонскому Финансовому Боту*

*🏛️ Основные принципы:*
• Каждый доход автоматически делится на 10% (Золотой запас) и 90% (Бюджет на жизнь)
• Расходы возможны ТОЛЬКО из Бюджета на жизнь (90%)
• Золотой запас НЕДОСТУПЕН для расходов

*📈 Финансовая аналитика:*
• 📊 Финансовый обзор - ключевые метрики и балансы
• 📈 Анализ расходов - детализация по категориям
• 💰 Динамика доходов - тренды и структура доходов
• 📉 Графики и отчеты - визуализация данных

*💡 Быстрые команды:*
• `10000 зарплата` - добавить доход
• `1500 еда обед` - добавить расход
• `-50000 аванс` - доход (отрицательная сумма)
• `долг Банк 50000` - добавить долг

*💎 Помни:* \"Сначала заплати себе - это основа финансовой свободы\"
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def show_debts_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню управления долгами при нажатии на кнопку 'Долги'"""
    user_id = update.message.from_user.id
    debts = debt_service.get_active_debts(user_id)
    
    menu_text = "🏛️ *Управление Долгами*\n\n"
    
    if not debts:
        menu_text += "🎉 *У вас нет активных долгов!*\n\n"
        menu_text += "💡 *Мудрость Вавилона:* «Свободный от долгов человек — уже богач!»"
    else:
        total_debt = sum(debt.current_amount for debt in debts)
        menu_text += f"📊 *Общая сумма долгов:* {total_debt:,.0f} руб.\n"
        menu_text += f"📋 *Количество долгов:* {len(debts)}\n\n"
        menu_text += "💡 *Выберите действие из меню ниже:*"
    
    from keyboards.main_menu import get_debt_management_keyboard
    await update.message.reply_text(
        menu_text, 
        parse_mode='Markdown',
        reply_markup=get_debt_management_keyboard()
    )

async def handle_menu_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды главного меню"""
    text = update.message.text
    
    if text == '💳 Добавить доход':
        return await add_income(update, context)
    elif text == '💸 Добавить расход':
        return await add_expense(update, context)
    elif text == '🏦 Мои кошельки':
        await show_wallets(update, context)
    elif text == '📈 Финансовая аналитика':  # ← ИЗМЕНИЛИ НАЗВАНИЕ
        await show_analytics_menu(update, context)  # ← ПЕРЕНОСИМ СЮДА
    elif text == '🏛️ Правила Вавилона':
        await show_babylon_rules(update, context)
    elif text == '📜 Долги':
        await show_debts_main_menu(update, context)
    elif text == 'ℹ️ Помощь':
        await show_help(update, context)
    else:
        # Пробуем быстрый ввод ТОЛЬКО если это не команда меню
        if not text.startswith(('📜', '➕', '💳', '📋', '📈', '🎯', '📊', '🏠', '🏛️', '🔮', '💰', '📉')):
            await quick_input(update, context)
        else:
            # Если это команда меню аналитики или долгов, но не обработалась - показываем помощь
            await update.message.reply_text(
                "❌ Команда не распознана. Используйте кнопки меню.",
                reply_markup=get_main_menu_keyboard()
            )

def _create_progress_bar(progress: float) -> str:
    """Создает текстовый прогресс-бар"""
    filled = '█' * int(progress / 10)
    empty = '░' * (10 - int(progress / 10))
    return f"{filled}{empty}"