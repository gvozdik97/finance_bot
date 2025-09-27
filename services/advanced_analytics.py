# services/advanced_analytics.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database.connection import db_connection
from services.wallet_service import wallet_service
from services.transaction_service import transaction_service
from services.debt_service import debt_service

logger = logging.getLogger(__name__)

class AdvancedAnalyticsService:
    """
    Продвинутая аналитика в стиле древнего Вавилона
    Финансовые метрики, KPI и умные рекомендации
    """
    
    def __init__(self):
        self.conn = db_connection
    
    def calculate_financial_health_score(self, user_id: int) -> Dict:
        """
        Рассчитывает общий индекс финансового здоровья (0-100)
        на основе вавилонских принципов
        """
        try:
            # Базовые метрики (получаем один раз)
            wallets = wallet_service.get_all_wallets(user_id)
            debts = debt_service.get_active_debts(user_id)
            transactions = transaction_service.get_transaction_history(user_id, 100)
            
            # 1. Правило 10% (Вес: 30%)
            rule_10_percent = self._calculate_10_percent_score(wallets, transactions)
            
            # 2. Контроль расходов (Вес: 25%)
            expense_control = self._calculate_expense_control_score(wallets, transactions)
            
            # 3. Свобода от долгов (Вес: 20%)
            debt_freedom = self._calculate_debt_freedom_score(debts)
            
            # 4. Стабильность доходов (Вес: 15%)
            income_stability = self._calculate_income_stability_score(transactions)
            
            # 5. Накопительные привычки (Вес: 10%)
            savings_habit = self._calculate_savings_habit_score(wallets, transactions)
            
            # Общий счет (взвешенная сумма)
            total_score = (
                rule_10_percent * 0.30 +
                expense_control * 0.25 +
                debt_freedom * 0.20 +
                income_stability * 0.15 +
                savings_habit * 0.10
            )
            
            # Генерируем рекомендации БЕЗ повторного вызова calculate_financial_health_score
            recommendations = self._generate_recommendations_direct(
                rule_10_percent, expense_control, debt_freedom, income_stability, savings_habit
            )
            
            return {
                'total_score': round(total_score, 1),
                'components': {
                    'rule_10_percent': round(rule_10_percent, 1),
                    'expense_control': round(expense_control, 1),
                    'debt_freedom': round(debt_freedom, 1),
                    'income_stability': round(income_stability, 1),
                    'savings_habit': round(savings_habit, 1)
                },
                'level': self._get_financial_level(total_score),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Financial health calculation error: {e}")
            return {
                'total_score': 0, 
                'components': {}, 
                'level': 'Новичок', 
                'recommendations': ['Начните с добавления первых транзакций']
            }
    
    def _calculate_10_percent_score(self, wallets: Dict, transactions: List) -> float:
        """Оценка соблюдения правила 10%"""
        gold_reserve = wallets.get('gold_reserve', 0)
        
        # Анализ доходов за последние 3 месяца
        recent_income = self._calculate_recent_income(transactions, days=90)
        
        if recent_income == 0:
            return 0.0
        
        actual_percentage = (gold_reserve / recent_income * 100) if recent_income > 0 else 0
        target_percentage = 10.0
        
        # Оценка: чем ближе к 10%, тем выше балл
        score = max(0, min(100, (actual_percentage / target_percentage * 100)))
        return score
    
    def _calculate_expense_control_score(self, wallets: Dict, transactions: List) -> float:
        """Оценка контроля расходов"""
        living_budget = wallets.get('living_budget', 0)
        
        # Анализ расходов за последний месяц
        recent_expenses = self._calculate_recent_expenses(transactions, days=30)
        
        if living_budget == 0:
            return 50.0  # Средний балл если нет данных
        
        # Идеал: расходы составляют 80-90% от бюджета жизни
        expense_ratio = (recent_expenses / living_budget * 100) if living_budget > 0 else 0
        ideal_min, ideal_max = 70, 90
        
        if expense_ratio < ideal_min:
            # Слишком мало тратим (возможно, не все учитываем)
            score = (expense_ratio / ideal_min * 100) * 0.8
        elif expense_ratio <= ideal_max:
            # Идеальный диапазон
            score = 100.0
        else:
            # Превышаем бюджет
            overspend = expense_ratio - ideal_max
            score = max(0, 100 - (overspend * 2))
        
        return score
    
    def _calculate_debt_freedom_score(self, debts: List) -> float:
        """Оценка свободы от долгов"""
        if not debts:
            return 100.0  # Нет долгов - идеальный счет
        
        total_debt = sum(debt.current_amount for debt in debts)
        total_initial = sum(debt.initial_amount for debt in debts)
        
        if total_initial == 0:
            return 0.0
        
        # Прогресс погашения (чем больше погашено, тем выше балл)
        progress = ((total_initial - total_debt) / total_initial * 100)
        
        # Учитываем также размер долговой нагрузки
        debt_burden_score = max(0, 100 - (total_debt / 10000))  # Упрощенная формула
        
        return (progress + debt_burden_score) / 2
    
    def _calculate_income_stability_score(self, transactions: List) -> float:
        """Оценка стабильности доходов"""
        income_transactions = [t for t in transactions if t[0] == 'income']
        
        if len(income_transactions) < 2:
            return 50.0  # Недостаточно данных
        
        # Берем последние 6 доходов (примерно 3 месяца)
        amounts = [t[1] for t in income_transactions[:6]]
        avg_income = sum(amounts) / len(amounts)
        
        if avg_income == 0:
            return 0.0
        
        # Коэффициент вариации (меньше = стабильнее)
        variance = sum((x - avg_income) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        cv = (std_dev / avg_income * 100)
        
        # Оценка: чем меньше вариация, тем выше балл
        score = max(0, 100 - min(cv, 100))  # Ограничиваем cv 100%
        return score
    
    def _calculate_savings_habit_score(self, wallets: Dict, transactions: List) -> float:
        """Оценка накопительных привычек"""
        gold_reserve = wallets.get('gold_reserve', 0)
        
        # Анализ регулярности пополнений
        savings_transactions = [t for t in transactions if t[0] == 'income']
        
        if not savings_transactions or gold_reserve == 0:
            return 0.0
        
        # Простая оценка: чем больше золотой запас относительно доходов, тем лучше
        recent_income = self._calculate_recent_income(transactions, days=90)
        if recent_income == 0:
            return 0.0
        
        savings_ratio = (gold_reserve / recent_income * 100)
        score = min(100, savings_ratio * 2)  # 50% соотношение = 100 баллов
        
        return score
    
    def _calculate_recent_income(self, transactions: List, days: int = 30) -> float:
        """Рассчитывает доходы за указанный период"""
        # Упрощенная версия - берем все доходы из переданных транзакций
        return sum(t[1] for t in transactions if t[0] == 'income')
    
    def _calculate_recent_expenses(self, transactions: List, days: int = 30) -> float:
        """Рассчитывает расходы за указанный период"""
        # Упрощенная версия - берем все расходы из переданных транзакций
        return sum(t[1] for t in transactions if t[0] == 'expense')
    
    def _get_financial_level(self, score: float) -> str:
        """Определяет уровень финансового здоровья"""
        if score >= 90:
            return "🏛️ Мудрец Вавилона"
        elif score >= 75:
            return "🥇 Золотой уровень"
        elif score >= 60:
            return "🥈 Серебряный уровень"
        elif score >= 40:
            return "🥉 Бронзовый уровень"
        else:
            return "🎯 Новичок"
    
    def _generate_recommendations_direct(self, rule_10: float, expense_ctrl: float, 
                                       debt_free: float, income_stab: float, savings: float) -> List[str]:
        """Генерирует рекомендации напрямую из компонентов (без рекурсии)"""
        recommendations = []
        
        # Общие рекомендации на основе общего уровня
        avg_score = (rule_10 + expense_ctrl + debt_free + income_stab + savings) / 5
        
        if avg_score < 60:
            recommendations.append("💡 *Совет Вавилона:* Начните с малого - откладывайте 10% от каждого дохода")
        
        if avg_score < 40:
            recommendations.append("🎯 *Приоритет:* Сконцентрируйтесь на создании золотого запаса")
        
        # Конкретные рекомендации по слабым компонентам
        if rule_10 < 80:
            recommendations.append("💰 *Улучшение:* Стремитесь к стабильному откладыванию 10% от доходов")
        
        if debt_free < 50:
            recommendations.append("🏛️ *Цель:* Разработайте план погашения долгов")
        
        if expense_ctrl < 60:
            recommendations.append("📊 *Анализ:* Изучите свои расходы для оптимизации")
        
        if income_stab < 50:
            recommendations.append("📈 *Развитие:* Рассмотрите возможности увеличения доходов")
        
        if len(recommendations) == 0:
            recommendations.append("🎉 *Отлично!* Продолжайте в том же духе!")
        
        return recommendations
    
    def predict_savings_timeline(self, user_id: int, target_amount: float) -> Dict:
        """
        Прогнозирует время достижения цели накоплений
        на основе текущих привычек
        """
        try:
            transactions = transaction_service.get_transaction_history(user_id, 90)
            wallets = wallet_service.get_all_wallets(user_id)
            
            # Анализ текущих темпов накопления
            monthly_income = self._calculate_monthly_income(transactions)
            monthly_savings = monthly_income * 0.10  # Предполагаем правило 10%
            
            current_savings = wallets.get('gold_reserve', 0)
            remaining = max(0, target_amount - current_savings)
            
            if monthly_savings <= 0:
                return {
                    'achievable': False,
                    'message': "❌ Недостаточно данных для прогноза. Добавьте данные о доходах."
                }
            
            months_needed = remaining / monthly_savings
            
            return {
                'achievable': True,
                'current_savings': current_savings,
                'monthly_savings': monthly_savings,
                'months_needed': months_needed,
                'estimated_date': (datetime.now() + timedelta(days=months_needed * 30)).strftime('%d.%m.%Y'),
                'recommendation': self._get_savings_recommendation(monthly_savings, target_amount)
            }
            
        except Exception as e:
            logger.error(f"Savings prediction error: {e}")
            return {'achievable': False, 'message': 'Ошибка расчета'}
    
    def _calculate_monthly_income(self, transactions: List) -> float:
        """Рассчитывает среднемесячный доход"""
        income_transactions = [t for t in transactions if t[0] == 'income']
        
        if not income_transactions:
            return 0.0
        
        # Берем доходы за последние 3 месяца (последние 6 транзакций)
        recent_income = sum(t[1] for t in income_transactions[:6])
        monthly_avg = recent_income / 3 if recent_income > 0 else 0
        
        return monthly_avg
    
    def _get_savings_recommendation(self, monthly_savings: float, target: float) -> str:
        """Генерирует рекомендацию по накоплениям"""
        if monthly_savings <= 0:
            return "💡 Начните с создания источника доходов"
        
        time_years = (target / monthly_savings) / 12
        
        if time_years > 5:
            return "🎯 Рассмотрите возможность увеличения доходов или экономии"
        elif time_years > 2:
            return "💪 Хороший темп! Продолжайте в том же духе"
        else:
            return "🚀 Отличные результаты! Цель близка"
    
    def analyze_spending_patterns(self, user_id: int) -> Dict:
        """
        Анализирует паттерны расходов и выявляет тенденции
        """
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            # Анализ по категориям за последние 30 дней
            cursor.execute('''
                SELECT category, SUM(amount) as total, COUNT(*) as count
                FROM transactions 
                WHERE user_id = ? AND type = 'expense' 
                AND date >= date('now', '-30 days')
                GROUP BY category
                ORDER BY total DESC
            ''', (user_id,))
            
            patterns = cursor.fetchall()
            conn.close()
            
            # Если нет данных за 30 дней, пробуем взять все данные
            if not patterns:
                conn = self.conn.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT category, SUM(amount) as total, COUNT(*) as count
                    FROM transactions 
                    WHERE user_id = ? AND type = 'expense'
                    GROUP BY category
                    ORDER BY total DESC
                ''', (user_id,))
                patterns = cursor.fetchall()
                conn.close()
            
            analysis = {
                'total_categories': len(patterns),
                'top_categories': [],
                'insights': [],
                'monthly_total': sum(row[1] for row in patterns)
            }
            
            for category, total, count in patterns[:5]:  # Топ-5 категорий
                analysis['top_categories'].append({
                    'category': category,
                    'amount': total,
                    'percentage': (total / analysis['monthly_total'] * 100) if analysis['monthly_total'] > 0 else 0,
                    'frequency': count
                })
            
            # Генерация инсайтов
            analysis['insights'] = self._generate_spending_insights(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Spending analysis error: {e}")
            return {
                'total_categories': 0,
                'top_categories': [],
                'insights': ['Недостаточно данных для анализа расходов'],
                'monthly_total': 0
            }
    
    def _generate_spending_insights(self, analysis: Dict) -> List[str]:
        """Генерирует инсайты на основе анализа расходов"""
        insights = []
        top_categories = analysis.get('top_categories', [])
        
        if not top_categories:
            insights.append("📊 Пока недостаточно данных для анализа расходов")
            return insights
        
        # Анализ распределения
        if len(top_categories) >= 3:
            top3_percentage = sum(cat['percentage'] for cat in top_categories[:3])
            if top3_percentage > 70:
                insights.append("🎯 Основные расходы сконцентрированы в 3-х категориях")
        
        # Поиск потенциальной экономии
        for category in top_categories:
            if category['percentage'] > 30:  # Если категория > 30%
                insights.append(f"💡 {category['category']} - крупная статья расходов")
        
        if len(insights) == 0:
            insights.append("✅ Расходы распределены сбалансированно")
        
        return insights

# Глобальный экземпляр сервиса
advanced_analytics = AdvancedAnalyticsService()