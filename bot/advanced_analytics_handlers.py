# bot/advanced_analytics_handlers.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.trend_analyzer import trend_analyzer
from utils.babylon_visualizers import babylon_visualizer
from keyboards.analytics_menu import get_advanced_analytics_menu_keyboard, get_visualizations_menu_keyboard

logger = logging.getLogger(__name__)

async def show_wealth_temple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает храм богатства"""
    user_id = update.message.from_user.id
    
    try:
        temple = babylon_visualizer.create_wealth_temple(user_id)
        # УБИРАЕМ parse_mode для сообщений с эмодзи и спецсимволами
        await update.message.reply_text(temple)  # Без parse_mode='Markdown'
        
    except Exception as e:
        logger.error(f"Temple visualization error: {e}")
        await update.message.reply_text("❌ Ошибка при создании храма")

async def show_financial_pyramid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает пирамиду финансовой стабильности"""
    user_id = update.message.from_user.id
    
    try:
        pyramid = babylon_visualizer.create_financial_pyramid(user_id)
        # УБИРАЕМ parse_mode для сообщений с эмодзи
        await update.message.reply_text(pyramid)  # Без parse_mode='Markdown'
        
    except Exception as e:
        logger.error(f"Pyramid visualization error: {e}")
        await update.message.reply_text("❌ Ошибка при создании пирамиды")

async def show_river_of_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает реки финансовой удачи"""
    user_id = update.message.from_user.id
    
    try:
        river = babylon_visualizer.create_river_of_fortune(user_id)
        # УБИРАЕМ parse_mode
        await update.message.reply_text(river)  # Без parse_mode='Markdown'
        
    except Exception as e:
        logger.error(f"River visualization error: {e}")
        await update.message.reply_text("❌ Ошибка при создании диаграммы рек")

async def show_zodiac_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает финансовый гороскоп"""
    user_id = update.message.from_user.id
    
    try:
        zodiac = babylon_visualizer.create_zodiac_financial_chart(user_id)
        # УБИРАЕМ parse_mode
        await update.message.reply_text(zodiac)  # Без parse_mode='Markdown'
        
    except Exception as e:
        logger.error(f"Zodiac visualization error: {e}")
        await update.message.reply_text("❌ Ошибка при создании гороскопа")

async def show_monthly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает месячный отчет"""
    user_id = update.message.from_user.id
    
    try:
        report = babylon_visualizer.create_monthly_report(user_id)
        # УБИРАЕМ parse_mode
        await update.message.reply_text(report)  # Без parse_mode='Markdown'
        
    except Exception as e:
        logger.error(f"Monthly report error: {e}")
        await update.message.reply_text("❌ Ошибка при создании отчета")

# Остальные функции остаются с parse_mode, так как у них простой текст
async def show_income_trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает анализ трендов доходов"""
    user_id = update.message.from_user.id
    
    try:
        trends = trend_analyzer.analyze_income_trends(user_id)
        
        if not trends['has_data']:
            await update.message.reply_text(
                trends['message'],
                reply_markup=get_advanced_analytics_menu_keyboard()
            )
            return
        
        trends_text = "*АНАЛИЗ ТРЕНДОВ ДОХОДОВ*\n\n"
        
        trends_text += f"*Направление тренда:* {trends['trend_direction'].capitalize()}\n"
        trends_text += f"*Волатильность:* {trends['volatility']:.1f}%\n"
        trends_text += f"*Темп роста:* {trends['growth_rate']:.1f}%\n"
        trends_text += f"*Средний доход:* {trends['average_income']:,.0f} руб./мес.\n"
        trends_text += f"*Последний месяц:* {trends['latest_income']:,.0f} руб.\n\n"
        
        trends_text += "*ПРОГНОЗ НА 3 МЕСЯЦА:*\n"
        trends_text += f"• Ожидаемый доход: {trends['forecast']['next_3_months']:,.0f} руб.\n"
        trends_text += f"• Прогноз: {trends['forecast']['outlook']}\n"
        trends_text += f"• Уверенность: {trends['forecast']['confidence']}\n\n"
        
        if trends['trend_direction'] == "растущий":
            trends_text += "🎉 *Отличные новости!* Ваши доходы растут!"
        elif trends['trend_direction'] == "падающий":
            trends_text += "💡 *Рекомендация:* Рассмотрите новые источники доходов"
        else:
            trends_text += "✅ *Стабильность* - хорошая основа для планирования"
        
        # ЭТОТ ТЕКСТ БЕЗОПАСЕН ДЛЯ MARKDOWN
        await update.message.reply_text(trends_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Income trends error: {e}")
        await update.message.reply_text("❌ Ошибка при анализе трендов доходов")

async def show_expense_patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает анализ паттернов расходов"""
    user_id = update.message.from_user.id
    
    try:
        patterns = trend_analyzer.analyze_expense_patterns(user_id)
        
        if not patterns['has_data']:
            await update.message.reply_text(
                patterns['message'],
                reply_markup=get_advanced_analytics_menu_keyboard()
            )
            return
        
        patterns_text = "*АНАЛИЗ ПАТТЕРНОВ РАСХОДОВ*\n\n"
        
        patterns_text += f"*Анализировано категорий:* {patterns['total_categories']}\n"
        patterns_text += f"*Средние расходы:* {patterns['average_monthly_expense']:,.0f} руб./мес.\n\n"
        
        patterns_text += "*ОСНОВНЫЕ ПАТТЕРНЫ:*\n"
        for i, pattern in enumerate(patterns['spending_patterns'][:5], 1):
            patterns_text += f"{i}. *{pattern['category']}*\n"
            patterns_text += f"   Тренд: {pattern['trend']}\n"
            patterns_text += f"   Волатильность: {pattern['volatility']:.1f}%\n"
            patterns_text += f"   В среднем: {pattern['average_amount']:,.0f} руб.\n\n"
        
        patterns_text += "*РЕКОМЕНДАЦИИ:*\n"
        for recommendation in patterns['recommendations']:
            patterns_text += f"• {recommendation}\n"
        
        # ЭТОТ ТЕКСТ БЕЗОПАСЕН ДЛЯ MARKDOWN
        await update.message.reply_text(patterns_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Expense patterns error: {e}")
        await update.message.reply_text("❌ Ошибка при анализе паттернов расходов")

async def show_visualizations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню визуализаций"""
    menu_text = """
*ВИЗУАЛИЗАЦИИ ВАВИЛОНА*

Выберите тип визуализации:

🏔️ Пирамида финансовой стабильности
🏛️ Храм вашего богатства  
🌊 Реки финансовой удачи
✨ Финансовый гороскоп
📜 Месячная летопись

*Мудрость Вавилона:* «Картина богатства складывается из многих деталей»
"""
    
    await update.message.reply_text(
        menu_text, 
        parse_mode='Markdown',
        reply_markup=get_visualizations_menu_keyboard()
    )