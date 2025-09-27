# bot/analytics_handlers.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.advanced_analytics import advanced_analytics
from utils.babylon_visualizers import babylon_visualizer
from keyboards.analytics_menu import get_advanced_analytics_menu_keyboard

logger = logging.getLogger(__name__)

async def show_financial_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает индекс финансового здоровья"""
    user_id = update.message.from_user.id
    
    try:
        health_data = advanced_analytics.calculate_financial_health_score(user_id)
        
        health_text = "*ИНДЕКС ФИНАНСОВОГО ЗДОРОВЬЯ*\n\n"
        
        # Общая оценка
        health_text += f"*Общий счет:* {health_data['total_score']}/100\n"
        health_text += f"*Уровень:* {health_data['level']}\n\n"
        
        # Детализация по компонентам
        health_text += "*Компоненты оценки:*\n"
        for component, score in health_data['components'].items():
            progress_bar = babylon_visualizer.create_progress_bar(score)
            component_name = {
                'rule_10_percent': 'Правило 10%',
                'expense_control': 'Контроль расходов', 
                'debt_freedom': 'Свобода от долгов',
                'income_stability': 'Стабильность доходов',
                'savings_habit': 'Накопительные привычки'
            }.get(component, component)
            
            health_text += f"{component_name}: {progress_bar}\n"
        
        health_text += "\n*Рекомендации:*\n"
        for recommendation in health_data['recommendations']:
            health_text += f"• {recommendation}\n"
        
        # Первое сообщение - с markdown (безопасный текст)
        await update.message.reply_text(health_text, parse_mode='Markdown')
        
        # Второе сообщение - пирамида БЕЗ markdown
        pyramid = babylon_visualizer.create_financial_pyramid(user_id)
        await update.message.reply_text(pyramid)  # Без parse_mode
        
    except Exception as e:
        logger.error(f"Financial health error: {e}")
        await update.message.reply_text("❌ Ошибка при расчете финансового здоровья")

async def show_spending_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализирует паттерны расходов"""
    user_id = update.message.from_user.id
    
    try:
        analysis = advanced_analytics.analyze_spending_patterns(user_id)
        
        if 'error' in analysis:
            await update.message.reply_text("❌ Недостаточно данных для анализа")
            return
        
        analysis_text = "*АНАЛИЗ ВАШИХ РАСХОДОВ*\n\n"
        analysis_text += f"*Всего за месяц:* {analysis['monthly_total']:,.0f} руб.\n"
        analysis_text += f"*Категорий:* {analysis['total_categories']}\n\n"
        
        analysis_text += "*Топ-категории расходов:*\n"
        for i, category in enumerate(analysis['top_categories'][:5], 1):
            analysis_text += f"{i}. {category['category']}: {category['amount']:,.0f} руб. ({category['percentage']:.1f}%)\n"
        
        analysis_text += "\n*Инсайты:*\n"
        for insight in analysis['insights']:
            analysis_text += f"• {insight}\n"
        
        # Первое сообщение - с markdown
        await update.message.reply_text(analysis_text, parse_mode='Markdown')
        
        # Второе сообщение - реки БЕЗ markdown
        river_diagram = babylon_visualizer.create_river_of_fortune(user_id)
        await update.message.reply_text(river_diagram)  # Без parse_mode
        
    except Exception as e:
        logger.error(f"Spending analysis error: {e}")
        await update.message.reply_text("❌ Ошибка при анализе расходов")

async def show_savings_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает прогноз накоплений"""
    user_id = update.message.from_user.id
    
    try:
        target_amount = 100000  # Примерная цель по умолчанию
        
        forecast = advanced_analytics.predict_savings_timeline(user_id, target_amount)
        
        if not forecast['achievable']:
            await update.message.reply_text(forecast['message'])
            return
        
        forecast_text = "🔮 *ПРОГНОЗ НАКОПЛЕНИЙ*\n\n"
        forecast_text += f"🎯 *Цель:* {target_amount:,.0f} руб.\n"
        forecast_text += f"💰 *Текущие накопления:* {forecast['current_savings']:,.0f} руб.\n"
        forecast_text += f"📈 *Ежемесячные накопления:* {forecast['monthly_savings']:,.0f} руб.\n\n"
        forecast_text += f"⏱️ *Время достижения:* {forecast['months_needed']:.1f} месяцев\n"
        forecast_text += f"📅 *Примерная дата:* {forecast['estimated_date']}\n\n"
        forecast_text += f"💡 *Рекомендация:* {forecast['recommendation']}"
        
        await update.message.reply_text(forecast_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Savings forecast error: {e}")
        await update.message.reply_text("❌ Ошибка при создании прогноза")

async def show_personal_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает персональные рекомендации"""
    user_id = update.message.from_user.id
    
    try:
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