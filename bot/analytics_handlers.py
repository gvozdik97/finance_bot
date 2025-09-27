# bot/analytics_handlers.py - ОБЪЕДИНЕННАЯ АНАЛИТИКА

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.financial_analytics import financial_analytics
from utils.financial_charts import financial_charts
from keyboards.analytics_menu import get_analytics_menu_keyboard

logger = logging.getLogger(__name__)

async def show_analytics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню аналитики"""
    menu_text = """
📈 *ФИНАНСОВАЯ АНАЛИТИКА*

Выберите тип анализа:

📊 *Финансовый обзор* - ключевые метрики и балансы
📈 *Анализ расходов* - детализация по категориям  
💰 *Динамика доходов* - тренды и структура доходов
📉 *Графики и отчеты* - визуализация данных

💡 *Все данные актуальны за последние 30 дней*
"""

    await update.message.reply_text(
        menu_text,
        parse_mode='Markdown',
        reply_markup=get_analytics_menu_keyboard()
    )

async def show_financial_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает общий финансовый обзор"""
    user_id = update.message.from_user.id
    
    try:
        overview = financial_analytics.get_financial_overview(user_id)
        
        if not overview['success']:
            await update.message.reply_text(
                "❌ Недостаточно данных для анализа. Добавьте несколько транзакций.",
                reply_markup=get_analytics_menu_keyboard()
            )
            return
        
        # Формируем текст обзора
        overview_text = "📊 *ФИНАНСОВЫЙ ОБЗОР*\n\n"
        
        # Основные метрики
        overview_text += f"💼 *Общий баланс:* {overview['total_balance']:,.0f} руб.\n"
        overview_text += f"💰 *Золотой запас:* {overview['gold_reserve']:,.0f} руб.\n"
        overview_text += f"💳 *Доходы (30 дней):* {overview['monthly_income']:,.0f} руб.\n"
        overview_text += f"💸 *Расходы (30 дней):* {overview['monthly_expenses']:,.0f} руб.\n\n"
        
        # Ключевые показатели
        overview_text += f"📈 *Накопления:* {overview['savings_rate']:.1f}% от доходов\n"
        overview_text += f"📉 *Расходы:* {overview['expense_ratio']:.1f}% от доходов\n"
        
        # Финансовый поток
        net_flow = overview['net_flow']
        if net_flow > 0:
            overview_text += f"💎 *Чистый приток:* +{net_flow:,.0f} руб.\n"
        else:
            overview_text += f"⚠️ *Чистый отток:* {net_flow:,.0f} руб.\n"
        
        # Оценка финансового здоровья
        if overview['savings_rate'] >= 10:
            overview_text += "\n✅ *Отлично!* Вы соблюдаете правило 10%\n"
        elif overview['savings_rate'] > 0:
            overview_text += f"\n💡 *Совет:* Стремитесь к 10% накоплений\n"
        else:
            overview_text += f"\n🎯 *Рекомендация:* Начните откладывать 10% от следующего дохода\n"
        
        await update.message.reply_text(
            overview_text,
            parse_mode='Markdown',
            reply_markup=get_analytics_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Financial overview error: {e}")
        await update.message.reply_text(
            "❌ Ошибка при формировании обзора",
            reply_markup=get_analytics_menu_keyboard()
        )

async def show_spending_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает детальный анализ расходов"""
    user_id = update.message.from_user.id
    
    try:
        analysis = financial_analytics.get_spending_analysis(user_id)
        
        if not analysis['success'] or analysis['total_expenses'] == 0:
            await update.message.reply_text(
                "📊 *АНАЛИЗ РАСХОДОВ*\n\nНет данных о расходах за последний период.",
                parse_mode='Markdown',
                reply_markup=get_analytics_menu_keyboard()
            )
            return
        
        # Создаем текстовую диаграмму
        chart = financial_charts.create_spending_by_category(analysis['categories'])
        
        # Добавляем общую статистику
        stats_text = f"\n💸 *ОБЩАЯ СТАТИСТИКА:*\n"
        stats_text += f"Всего расходов: {analysis['total_expenses']:,.0f} руб.\n"
        stats_text += f"Категорий: {analysis['category_count']}\n"
        stats_text += f"Период: последние 30 дней\n\n"
        
        # Инсайты
        if analysis['category_count'] > 0:
            top_category = analysis['categories'][0]
            if top_category['percentage'] > 50:
                stats_text += f"💡 Основные расходы в категории: {top_category['name']}\n"
            elif analysis['category_count'] <= 3:
                stats_text += "💡 Расходы сконцентрированы в нескольких категориях\n"
            else:
                stats_text += "💡 Расходы распределены достаточно равномерно\n"
        
        full_text = chart + stats_text
        
        await update.message.reply_text(
            full_text,
            parse_mode='Markdown',
            reply_markup=get_analytics_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Spending analysis error: {e}")
        await update.message.reply_text(
            "❌ Ошибка при анализе расходов",
            reply_markup=get_analytics_menu_keyboard()
        )

async def show_income_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает анализ доходов"""
    user_id = update.message.from_user.id
    
    try:
        analysis = financial_analytics.get_income_analysis(user_id)
        
        if not analysis['success'] or analysis['total_income'] == 0:
            await update.message.reply_text(
                "💰 *АНАЛИЗ ДОХОДОВ*\n\nНет данных о доходах за последний период.",
                parse_mode='Markdown',
                reply_markup=get_analytics_menu_keyboard()
            )
            return
        
        income_text = "💰 *АНАЛИЗ ДОХОДОВ*\n\n"
        
        # Общая статистика
        income_text += f"💳 *Общая сумма:* {analysis['total_income']:,.0f} руб.\n"
        income_text += f"📅 *Период анализа:* {analysis['months_analyzed']} месяцев\n"
        income_text += f"📈 *Тренд:* {analysis['trend'].capitalize()}\n\n"
        
        # Динамика по месяцам
        if analysis['monthly_income']:
            income_text += "📊 *ПОСЛЕДНИЕ МЕСЯЦЫ:*\n"
            for month, amount in analysis['monthly_income'][:3]:  # Последние 3 месяца
                month_name = month[5:7]  # Берем только номер месяца
                income_text += f"{month_name}. {amount:,.0f} руб.\n"
            income_text += "\n"
        
        # Структура по категориям
        if analysis['income_by_category']:
            income_text += "🏷️ *ПО КАТЕГОРИЯМ:*\n"
            for category, amount in analysis['income_by_category'][:4]:  # Топ-4 категории
                percentage = (amount / analysis['total_income'] * 100) if analysis['total_income'] > 0 else 0
                income_text += f"• {category}: {amount:,.0f} руб. ({percentage:.1f}%)\n"
        
        await update.message.reply_text(
            income_text,
            parse_mode='Markdown',
            reply_markup=get_analytics_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Income analysis error: {e}")
        await update.message.reply_text(
            "❌ Ошибка при анализе доходов",
            reply_markup=get_analytics_menu_keyboard()
        )

async def show_financial_charts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает графики и визуализации"""
    user_id = update.message.from_user.id
    
    try:
        # Получаем данные для графиков
        overview = financial_analytics.get_financial_overview(user_id)
        spending_analysis = financial_analytics.get_spending_analysis(user_id)
        income_analysis = financial_analytics.get_income_analysis(user_id)
        
        charts_text = "📉 *ГРАФИКИ И ОТЧЕТЫ*\n\n"
        
        # График доходы vs расходы
        if overview['success'] and overview['monthly_income'] > 0:
            income_vs_expenses = financial_charts.create_income_vs_expenses(
                overview['monthly_income'], 
                overview['monthly_expenses']
            )
            charts_text += income_vs_expenses + "\n\n"
        
        # График прогресса накоплений
        if overview['success']:
            savings_chart = financial_charts.create_savings_progress(
                overview['gold_reserve'],
                overview['monthly_income']
            )
            charts_text += savings_chart + "\n\n"
        
        # Динамика по месяцам
        if income_analysis['success'] and income_analysis['monthly_income']:
            trend_chart = financial_charts.create_monthly_trend(income_analysis['monthly_income'])
            charts_text += trend_chart
        
        await update.message.reply_text(
            charts_text,
            parse_mode='Markdown',
            reply_markup=get_analytics_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Financial charts error: {e}")
        await update.message.reply_text(
            "❌ Ошибка при создании графиков",
            reply_markup=get_analytics_menu_keyboard()
        )

async def handle_analytics_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды меню аналитики"""
    text = update.message.text
    
    if text == '📊 Финансовый обзор':
        await show_financial_overview(update, context)
    elif text == '📈 Анализ расходов':
        await show_spending_analysis(update, context)
    elif text == '💰 Динамика доходов':
        await show_income_analysis(update, context)
    elif text == '📉 Графики и отчеты':
        await show_financial_charts(update, context)
    elif text == '🏠 Главное меню':
        from .common import show_main_menu
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "❌ Команда не распознана",
            reply_markup=get_analytics_menu_keyboard()
        )