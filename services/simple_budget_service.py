# services/simple_budget_service.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import logging
from typing import Dict, List, Optional
from database.connection import db_connection

logger = logging.getLogger(__name__)

class SimpleBudgetService:
    """
    Простой сервис бюджетов в рамках вавилонской философии.
    Бюджеты работают ТОЛЬКО с расходами из 90%.
    """
    
    def set_category_limit(self, user_id: int, category: str, monthly_limit: float) -> bool:
        """Устанавливает месячный лимит для категории расходов"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO budgets (user_id, category, amount, period)
                    VALUES (?, ?, ?, 'monthly')
                ''', (user_id, category, monthly_limit))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Budget set error: {e}")
            return False
    
    def get_category_limit(self, user_id: int, category: str) -> Optional[float]:
        """Получает лимит для категории"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT amount FROM budgets 
                    WHERE user_id = ? AND category = ?
                ''', (user_id, category))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Budget get error: {e}")
            return None
    
    def check_spending(self, user_id: int, category: str, new_expense: float) -> Dict:
        """
        Проверяет, не превысит ли новый расход лимит категории.
        Работает ТОЛЬКО в рамках текущего месяца.
        """
        monthly_limit = self.get_category_limit(user_id, category)
        
        if not monthly_limit:
            return {'has_limit': False}
        
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Получаем текущие расходы за месяц
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) 
                    FROM transactions 
                    WHERE user_id = ? AND category = ? AND type = 'expense'
                    AND date >= date('now', 'start of month')
                ''', (user_id, category))
                
                current_spent = cursor.fetchone()[0]
                
                total_after_expense = current_spent + new_expense
                exceeded = total_after_expense > monthly_limit
                overspend = max(0, total_after_expense - monthly_limit)
                
                return {
                    'has_limit': True,
                    'monthly_limit': monthly_limit,
                    'current_spent': current_spent,
                    'total_after_expense': total_after_expense,
                    'exceeded': exceeded,
                    'overspend': overspend,
                    'percent_used': (current_spent / monthly_limit * 100) if monthly_limit > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Spending check error: {e}")
            return {'has_limit': False}
    
    def get_all_limits(self, user_id: int) -> Dict[str, float]:
        """Получает все установленные лимиты пользователя"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT category, amount FROM budgets WHERE user_id = ?
                ''', (user_id,))
                
                limits = {row[0]: row[1] for row in cursor.fetchall()}
                return limits
                
        except Exception as e:
            logger.error(f"Get all limits error: {e}")
            return {}

# Глобальный экземпляр
simple_budget_service = SimpleBudgetService()