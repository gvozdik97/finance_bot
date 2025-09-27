# bot/handlers.py - ОБНОВЛЕННАЯ ВЕРСИЯ С АНАЛИТИКОЙ

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.wallet_service import wallet_service
from services.babylon_service import babylon_service
from services.transaction_service import transaction_service
from services.simple_budget_service import simple_budget_service
from services.debt_service import debt_service

from keyboards.main_menu import get_main_menu_keyboard, get_analytics_menu_keyboard, remove_keyboard
from .common import show_main_menu
from .analytics_handlers import show_financial_health, show_savings_forecast, show_spending_analysis

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

async def show_simple_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простая вавилонская статистика"""
    user_id = update.message.from_user.id
    
    try:
        wallets = wallet_service.get_all_wallets(user_id)
        transactions = transaction_service.get_transaction_history(user_id, 50)
        
        if not transactions:
            stats_text = "📊 *Простая статистика*\n\nЕще нет данных для анализа."
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            return
        
        income_total = sum(t[1] for t in transactions if t[0] == 'income')
        expense_total = sum(t[1] for t in transactions if t[0] == 'expense')
        gold_reserve_ratio = (wallets['gold_reserve'] / income_total * 100) if income_total > 0 else 0
        
        stats_text = f"""
📊 *Простая Вавилонская Статистика*

*Накопления:*
💰 Золотой запас: {wallets['gold_reserve']:,.0f} руб.
📈 Накоплено: {gold_reserve_ratio:.1f}% от доходов

*Общие показатели:*
✅ Всего доходов: {income_total:,.0f} руб.
❌ Всего расходов: {expense_total:,.0f} руб.
💼 Текущий баланс: {sum(wallets.values()):,.0f} руб.

*Последние операции:*
"""
        for i, (t_type, amount, category, desc, date) in enumerate(transactions[:5]):
            emoji = "💳" if t_type == 'income' else "💸"
            stats_text += f"{emoji} {amount:,.0f} руб. - {category}\n"
        
        if gold_reserve_ratio >= 10:
            stats_text += f"\n🎉 *Отлично!* Вы соблюдаете правило 10%!"
        else:
            stats_text += f"\n💡 *Совет:* Стремитесь к 10% накоплений от доходов"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики.")

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

async def show_analytics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню расширенной аналитики"""
    menu_text = """
📈 *РАСШИРЕННАЯ АНАЛИТИКА ВАВИЛОНА*

Выберите тип анализа:

🏛️ *Финансовое здоровье* - общая оценка по вавилонским меркам
🔮 *Прогноз накоплений* - когда достигнете финансовых целей
📊 *Анализ расходов* - паттерны и возможности для оптимизации
🎯 *Рекомендации* - персональные советы для улучшения

💡 *Мудрость Вавилона:* «Анализ расходов — первый шаг к богатству»
"""
    
    await update.message.reply_text(
        menu_text, 
        parse_mode='Markdown',
        reply_markup=get_analytics_menu_keyboard()
    )

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простая помощь по вавилонскому боту"""
    help_text = """
ℹ️ *Помощь по Вавилонскому Финансовому Боту*

*🏛️ Основные принципы:*
• Каждый доход автоматически делится на 10% (Золотой запас) и 90% (Бюджет на жизнь)
• Расходы возможны ТОЛЬКО из Бюджета на жизнь (90%)
• Золотой запас НЕДОСТУПЕН для расходов

*📈 Новые возможности аналитики:*
• 🏛️ Финансовое здоровье - оценка по вавилонским стандартам
• 🔮 Прогноз накоплений - планирование финансовых целей  
• 📊 Анализ расходов - умные инсайты о ваших тратах
• 🎯 Рекомендации - персональные советы для улучшения

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
    elif text == '📊 Простая статистика':
        await show_simple_stats(update, context)
    elif text == '📈 Финансовая аналитика':  # ✅ НОВАЯ КНОПКА
        await show_analytics_menu(update, context)
    elif text == '🏛️ Правила Вавилона':
        await show_babylon_rules(update, context)
    elif text == '📜 Долги':
        await show_debts_main_menu(update, context)
    elif text == 'ℹ️ Помощь':
        await show_help(update, context)
    else:
        # Пробуем быстрый ввод ТОЛЬКО если это не команда меню
        if not text.startswith(('📜', '➕', '💳', '📋', '📈', '🎯', '📊', '🏠', '🏛️', '🔮')):
            await quick_input(update, context)
        else:
            # Если это команда меню аналитики или долгов, но не обработалась - показываем помощь
            await update.message.reply_text(
                "❌ Команда не распознана. Используйте кнопки меню.",
                reply_markup=get_main_menu_keyboard()
            )

async def handle_analytics_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды меню аналитики"""
    text = update.message.text
    
    if text == '🏛️ Финансовое здоровье':
        await show_financial_health(update, context)
    elif text == '🔮 Прогноз накоплений':
        await show_savings_forecast(update, context)
    elif text == '📊 Анализ расходов':
        await show_spending_analysis(update, context)
    elif text == '🎯 Персональные рекомендации':
        await show_personal_recommendations(update, context)
    elif text == '🏠 Главное меню':
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "❌ Команда аналитики не распознана.",
            reply_markup=get_analytics_menu_keyboard()
        )

async def show_personal_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает персональные рекомендации"""
    user_id = update.message.from_user.id
    
    try:
        from services.advanced_analytics import advanced_analytics
        
        # Получаем данные БЕЗ рекурсии
        health_data = advanced_analytics.calculate_financial_health_score(user_id)
        
        rec_text = "🎯 *ПЕРСОНАЛЬНЫЕ РЕКОМЕНДАЦИИ ВАВИЛОНА*\n\n"
        rec_text += f"💎 *Ваш уровень:* {health_data['level']}\n"
        rec_text += f"📊 *Общий счет:* {health_data['total_score']}/100\n\n"
        
        rec_text += "💡 *Рекомендации для улучшения:*\n"
        for i, recommendation in enumerate(health_data['recommendations'], 1):
            rec_text += f"{i}. {recommendation}\n"
        
        # Дополнительные рекомендации на основе слабых мест
        if health_data['components']:
            weakest_component = min(health_data['components'].items(), key=lambda x: x[1])
            rec_text += f"\n🎯 *Приоритетное улучшение:*\n"
            
            if weakest_component[0] == 'rule_10_percent':
                rec_text += "Сфокусируйтесь на правиле 10%. Начните с малого - откладывайте с каждого дохода."
            elif weakest_component[0] == 'expense_control':
                rec_text += "Проанализируйте расходы. Возможно, есть категории где можно сэкономить."
            elif weakest_component[0] == 'debt_freedom':
                rec_text += "Разработайте план погашения долгов. Маленькие победы придают сил!"
            elif weakest_component[0] == 'income_stability':
                rec_text += "Рассмотрите возможности увеличения доходов или создания дополнительных источников."
        
        rec_text += f"\n\n💪 *Совет Вавилона:* «Улучшайте по одному компоненту за раз!»"
        
        await update.message.reply_text(rec_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        await update.message.reply_text(
            "💡 *Совет Вавилона:* Начните с добавления первых доходов и расходов для получения персонализированных рекомендаций.",
            parse_mode='Markdown'
        )

def _create_progress_bar(progress: float) -> str:
    """Создает текстовый прогресс-бар"""
    filled = '█' * int(progress / 10)
    empty = '░' * (10 - int(progress / 10))
    return f"{filled}{empty}"

from .conversations import add_income, add_expense, quick_input