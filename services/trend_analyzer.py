# services/trend_analyzer.py - НОВЫЙ СЕРВИС АНАЛИТИКИ ТРЕНДОВ

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database.connection import db_connection

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """
    Анализатор финансовых трендов и прогнозов
    с использованием методов временных рядов
    """
    
    def __init__(self):
        self.conn = db_connection
    
    def analyze_income_trends(self, user_id: int) -> Dict:
        """
        Анализирует тренды доходов за последние 6 месяцев
        """
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            # Получаем доходы за последние 6 месяцев
            cursor.execute('''
                SELECT strftime('%Y-%m', date) as month, 
                       SUM(amount) as monthly_income
                FROM transactions 
                WHERE user_id = ? AND type = 'income'
                AND date >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month DESC
            ''', (user_id,))
            
            monthly_data = cursor.fetchall()
            conn.close()
            
            if len(monthly_data) < 2:
                return {
                    'has_data': False,
                    'message': 'Недостаточно данных для анализа трендов'
                }
            
            # Анализ тренда
            months = [row[0] for row in monthly_data]
            incomes = [row[1] for row in monthly_data]
            
            # Простой линейный тренд
            trend_direction = self._calculate_trend_direction(incomes)
            volatility = self._calculate_volatility(incomes)
            growth_rate = self._calculate_growth_rate(incomes)
            
            return {
                'has_data': True,
                'trend_direction': trend_direction,
                'volatility': volatility,
                'growth_rate': growth_rate,
                'average_income': sum(incomes) / len(incomes),
                'latest_income': incomes[0],
                'months_analyzed': len(months),
                'forecast': self._generate_income_forecast(incomes, trend_direction)
            }
            
        except Exception as e:
            logger.error(f"Income trend analysis error: {e}")
            return {'has_data': False, 'message': 'Ошибка анализа'}
    
    def analyze_expense_patterns(self, user_id: int) -> Dict:
        """
        Анализирует паттерны расходов и выявляет сезонность
        """
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            # Анализ по категориям и месяцам
            cursor.execute('''
                SELECT category, strftime('%Y-%m', date) as month,
                       SUM(amount) as monthly_expense
                FROM transactions 
                WHERE user_id = ? AND type = 'expense'
                AND date >= date('now', '-6 months')
                GROUP BY category, strftime('%Y-%m', date)
                ORDER BY month DESC, monthly_expense DESC
            ''', (user_id,))
            
            category_data = cursor.fetchall()
            conn.close()
            
            if not category_data:
                return {'has_data': False, 'message': 'Нет данных о расходах'}
            
            # Анализ сезонности и паттернов
            patterns = self._identify_spending_patterns(category_data)
            recommendations = self._generate_expense_recommendations(patterns)
            
            return {
                'has_data': True,
                'total_categories': len(set(row[0] for row in category_data)),
                'spending_patterns': patterns,
                'recommendations': recommendations,
                'average_monthly_expense': self._calculate_average_expense(category_data)
            }
            
        except Exception as e:
            logger.error(f"Expense pattern analysis error: {e}")
            return {'has_data': False, 'message': 'Ошибка анализа'}
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Определяет направление тренда"""
        if len(values) < 2:
            return "неопределенный"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first * 1.1:
            return "растущий"
        elif avg_second < avg_first * 0.9:
            return "падающий"
        else:
            return "стабильный"
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Рассчитывает волатильность данных"""
        if len(values) < 2:
            return 0.0
        
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        return (variance ** 0.5) / avg * 100  # Коэффициент вариации в %
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Рассчитывает средний темп роста"""
        if len(values) < 2:
            return 0.0
        
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                growth_rate = (values[i] - values[i-1]) / values[i-1] * 100
                growth_rates.append(growth_rate)
        
        return sum(growth_rates) / len(growth_rates) if growth_rates else 0.0
    
    def _generate_income_forecast(self, historical_data: List[float], trend: str) -> Dict:
        """Генерирует простой прогноз доходов"""
        if not historical_data:
            return {'message': 'Недостаточно данных для прогноза'}
        
        last_value = historical_data[0]
        avg_growth = self._calculate_growth_rate(historical_data)
        
        if trend == "растущий":
            forecast_3m = last_value * (1 + avg_growth/100 * 3)
            outlook = "оптимистичный"
        elif trend == "падающий":
            forecast_3m = last_value * (1 - abs(avg_growth)/100 * 3)
            outlook = "осторожный"
        else:
            forecast_3m = last_value
            outlook = "стабильный"
        
        return {
            'next_3_months': max(0, forecast_3m),
            'outlook': outlook,
            'confidence': 'средняя' if len(historical_data) >= 3 else 'низкая'
        }
    
    def _identify_spending_patterns(self, category_data: List) -> List[Dict]:
        """Выявляет паттерны расходов"""
        patterns = []
        
        # Группируем по категориям
        categories = {}
        for category, month, amount in category_data:
            if category not in categories:
                categories[category] = []
            categories[category].append((month, amount))
        
        for category, monthly_data in categories.items():
            if len(monthly_data) >= 2:
                amounts = [amount for month, amount in monthly_data]
                trend = self._calculate_trend_direction(amounts)
                volatility = self._calculate_volatility(amounts)
                
                patterns.append({
                    'category': category,
                    'trend': trend,
                    'volatility': volatility,
                    'average_amount': sum(amounts) / len(amounts),
                    'latest_amount': amounts[0]
                })
        
        return sorted(patterns, key=lambda x: x['latest_amount'], reverse=True)
    
    def _generate_expense_recommendations(self, patterns: List[Dict]) -> List[str]:
        """Генерирует рекомендации по расходам"""
        recommendations = []
        
        for pattern in patterns[:3]:  # Топ-3 категории
            if pattern['trend'] == "растущий" and pattern['volatility'] > 50:
                recommendations.append(
                    f"💡 {pattern['category']}: высокий рост и волатильность - рассмотрите оптимизацию"
                )
            elif pattern['volatility'] > 80:
                recommendations.append(
                    f"🎯 {pattern['category']}: нестабильные расходы - установите лимит"
                )
        
        if not recommendations:
            recommendations.append("✅ Расходы выглядят стабильно - продолжайте в том же духе!")
        
        return recommendations
    
    def _calculate_average_expense(self, category_data: List) -> float:
        """Рассчитывает средние месячные расходы"""
        monthly_totals = {}
        for category, month, amount in category_data:
            if month not in monthly_totals:
                monthly_totals[month] = 0
            monthly_totals[month] += amount
        
        if monthly_totals:
            return sum(monthly_totals.values()) / len(monthly_totals)
        return 0.0

# Глобальный экземпляр анализатора
trend_analyzer = TrendAnalyzer()