# finance_bot/database/connection.py

import sqlite3
import logging

class DatabaseConnection:
    def __init__(self, db_path='finance.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализирует таблицы базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица транзакций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                type TEXT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица бюджетов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                category TEXT,
                amount REAL,
                period TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info("Database initialized successfully")
    
    def get_connection(self):
        """Возвращает соединение с базой данных"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

# Глобальный экземпляр для использования во всем приложении
db_connection = DatabaseConnection()