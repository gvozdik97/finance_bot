# finance_bot/services/transaction_service.py

import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from database.connection import db_connection
from database.models import Transaction

class TransactionService:
    def __init__(self):
        self.conn = db_connection
    
    def add_transaction(self, user_id: int, transaction_type: str, amount: float, 
                       category: str, description: str = "Без описания") -> bool:
        """Добавляет новую транзакцию"""
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (user_id, type, amount, category, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, transaction_type, amount, category, description))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_user_transactions(self, user_id: int, days: Optional[int] = None, 
                            start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> List[Transaction]:
        """Получает транзакции пользователя за период"""
        conn = self.conn.get_connection()
        
        query = '''
            SELECT id, user_id, type, amount, category, description, date
            FROM transactions 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if days:
            query += " AND date > datetime('now', ?)"
            params.append(f'-{days} days')
        elif start_date and end_date:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += " ORDER BY date DESC"
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append(Transaction(*row))
        
        return transactions
    
    def get_transactions_summary(self, user_id: int, days: Optional[int] = None) -> dict:
        """Возвращает сводку по транзакциям"""
        transactions = self.get_user_transactions(user_id, days)
        
        income = sum(t.amount for t in transactions if t.type == 'income')
        expense = sum(t.amount for t in transactions if t.type == 'expense')
        margin = income - expense
        margin_percent = (margin / income * 100) if income > 0 else 0
        
        return {
            'income': income,
            'expense': expense,
            'margin': margin,
            'margin_percent': margin_percent,
            'transaction_count': len(transactions)
        }
    
    def get_category_spending(self, user_id: int, category: str, days: int = 30) -> float:
        """Возвращает сумму расходов по категории за период"""
        conn = self.conn.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE user_id = ? AND category = ? AND type = 'expense' 
            AND date > datetime('now', ?)
        ''', (user_id, category, f'-{days} days'))
        result = cursor.fetchone()[0]
        conn.close()
        return result

# Глобальный экземпляр сервиса
transaction_service = TransactionService()