# finance_bot/services/budget_service.py

import sqlite3
from typing import List, Optional, Tuple
from database.connection import db_connection
from database.models import Budget
from services.transaction_service import transaction_service

class BudgetService:
    def __init__(self):
        self.conn = db_connection
    
    def add_budget(self, user_id: int, category: str, amount: float, period: str = 'monthly') -> bool:
        """Добавляет новый бюджет"""
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO budgets (user_id, category, amount, period)
                VALUES (?, ?, ?, ?)
            ''', (user_id, category, amount, period))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding budget: {e}")
            return False
    
    def update_budget(self, user_id: int, category: str, amount: float) -> bool:
        """Обновляет существующий бюджет"""
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE budgets SET amount = ?, created_at = CURRENT_TIMESTAMP 
                WHERE user_id = ? AND category = ?
            ''', (amount, user_id, category))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating budget: {e}")
            return False
    
    def delete_budget(self, user_id: int, category: str) -> bool:
        """Удаляет бюджет"""
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting budget: {e}")
            return False
    
    def get_user_budgets(self, user_id: int) -> List[Budget]:
        """Получает все бюджеты пользователя"""
        conn = self.conn.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_id, category, amount, period, created_at FROM budgets WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        budgets = []
        for row in rows:
            budgets.append(Budget(*row))
        
        return budgets
    
    def get_budget(self, user_id: int, category: str) -> Optional[Budget]:
        """Получает бюджет по категории"""
        conn = self.conn.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_id, category, amount, period, created_at FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Budget(*row)
        return None
    
    def check_budget_exceeded(self, user_id: int, category: str, new_expense: float) -> dict:
        """Проверяет превышение бюджета"""
        budget = self.get_budget(user_id, category)
        if not budget:
            return {'exceeded': False}
        
        period_days = 30 if budget.period == 'monthly' else 7
        spent = transaction_service.get_category_spending(user_id, category, period_days)
        total_spent = spent + new_expense
        
        exceeded = total_spent > budget.amount
        overspend = max(0, total_spent - budget.amount)
        percent = (total_spent / budget.amount * 100) if budget.amount > 0 else 0
        
        return {
            'exceeded': exceeded,
            'budget_amount': budget.amount,
            'current_spent': spent,
            'total_after_transaction': total_spent,
            'overspend': overspend,
            'percent': percent
        }

# Глобальный экземпляр сервиса
budget_service = BudgetService()