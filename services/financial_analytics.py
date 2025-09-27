# services/financial_analytics.py - ПРАКТИЧНАЯ АНАЛИТИКА

import logging
from datetime import datetime, timedelta
from typing import Dict, List
from database.connection import db_connection

logger = logging.getLogger(__name__)

class FinancialAnalytics:
    """
    Практичная аналитика для повседневного использования
    """
    
    def __init__(self):
        self.conn = db_connection
    
    def get_financial_overview(self, user_id: int) -> Dict:
        """
        Комплексный финансовый обзор пользователя
        """
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            # Получаем текущие балансы кошельков
            cursor.execute('''
                SELECT wallet_type, balance FROM wallets WHERE user_id = ?
            ''', (user_id,))
            wallets = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Доходы за последние 30 дней
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM transactions 
                WHERE user_id = ? AND type = 'income' 
                AND date >= date('now', '-30 days')
            ''', (user_id,))
            monthly_income = cursor.fetchone()[0]
            
            # Расходы за последние 30 дней
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM transactions 
                WHERE user_id = ? AND type = 'expense' 
                AND date >= date('now', '-30 days')
            ''', (user_id,))
            monthly_expenses = cursor.fetchone()[0]
            
            # Накопления (золотой запас)
            gold_reserve = wallets.get('gold_reserve', 0)
            
            # Расчет ключевых метрик
            savings_rate = (gold_reserve / monthly_income * 100) if monthly_income > 0 else 0
            expense_ratio = (monthly_expenses / monthly_income * 100) if monthly_income > 0 else 0
            
            conn.close()
            
            return {
                'success': True,
                'wallets': wallets,
                'monthly_income': monthly_income,
                'monthly_expenses': monthly_expenses,
                'gold_reserve': gold_reserve,
                'savings_rate': savings_rate,
                'expense_ratio': expense_ratio,
                'net_flow': monthly_income - monthly_expenses,
                'total_balance': sum(wallets.values()) if wallets else 0
            }
            
        except Exception as e:
            logger.error(f"Financial overview error: {e}")
            return {'success': False, 'error': 'Ошибка расчета'}
    
    def get_spending_analysis(self, user_id: int) -> Dict:
        """
        Детальный анализ расходов по категориям
        """
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            # Расходы по категориям за последние 30 дней
            cursor.execute('''
                SELECT category, SUM(amount) as total, COUNT(*) as count
                FROM transactions 
                WHERE user_id = ? AND type = 'expense'
                AND date >= date('now', '-30 days')
                GROUP BY category
                ORDER BY total DESC
            ''', (user_id,))
            
            categories_data = cursor.fetchall()
            total_expenses = sum(row[1] for row in categories_data)
            
            # Если нет данных за 30 дней, берем все данные
            if not categories_data:
                cursor.execute('''
                    SELECT category, SUM(amount) as total, COUNT(*) as count
                    FROM transactions 
                    WHERE user_id = ? AND type = 'expense'
                    GROUP BY category
                    ORDER BY total DESC
                ''', (user_id,))
                categories_data = cursor.fetchall()
                total_expenses = sum(row[1] for row in categories_data)
            
            # Форматируем данные по категориям
            categories = []
            for category, total, count in categories_data:
                percentage = (total / total_expenses * 100) if total_expenses > 0 else 0
                categories.append({
                    'name': category,
                    'amount': total,
                    'percentage': percentage,
                    'count': count
                })
            
            conn.close()
            
            return {
                'success': True,
                'total_expenses': total_expenses,
                'categories': categories,
                'category_count': len(categories)
            }
            
        except Exception as e:
            logger.error(f"Spending analysis error: {e}")
            return {'success': False, 'error': 'Ошибка анализа расходов'}
    
    def get_income_analysis(self, user_id: int) -> Dict:
        """
        Анализ динамики и структуры доходов
        """
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            # Доходы по месяцам за последние 6 месяцев
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
            
            # Доходы по категориям
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM transactions 
                WHERE user_id = ? AND type = 'income'
                AND date >= date('now', '-90 days')
                GROUP BY category
                ORDER BY total DESC
            ''', (user_id,))
            
            category_data = cursor.fetchall()
            total_income = sum(row[1] for row in category_data)
            
            conn.close()
            
            # Анализ трендов
            trend = "стабильный"
            if len(monthly_data) >= 2:
                recent = monthly_data[0][1] if monthly_data else 0
                previous = monthly_data[1][1] if len(monthly_data) > 1 else 0
                if previous > 0:
                    change = ((recent - previous) / previous * 100)
                    if change > 10:
                        trend = "растущий"
                    elif change < -10:
                        trend = "падающий"
            
            return {
                'success': True,
                'monthly_income': monthly_data,
                'income_by_category': category_data,
                'total_income': total_income,
                'trend': trend,
                'months_analyzed': len(monthly_data)
            }
            
        except Exception as e:
            logger.error(f"Income analysis error: {e}")
            return {'success': False, 'error': 'Ошибка анализа доходов'}

# Глобальный экземпляр
financial_analytics = FinancialAnalytics()