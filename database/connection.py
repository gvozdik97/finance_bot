# finance_bot/database/connection.py

import sqlite3
import logging

class DatabaseConnection:
    def __init__(self, db_path='finance.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализирует таблицы базы данных с вавилонскими таблицами"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица транзакций (существующая)
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
        
        # Таблица бюджетов (существующая)
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
        
        # === НОВЫЕ ТАБЛИЦЫ ДЛЯ ВАВИЛОНСКОЙ СИСТЕМЫ ===
        
        # Таблица кошельков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                wallet_type TEXT,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, wallet_type)
            )
        ''')
        
        # Таблица прогресса правил
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS babylon_rules (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                rule_name TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                progress REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, rule_name)
            )
        ''')
        
        # Таблица долгов (для Фазы 2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                creditor TEXT,
                initial_amount REAL,
                current_amount REAL,
                interest_rate REAL DEFAULT 0.0,
                due_date TIMESTAMP,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debt_payments (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                debt_id INTEGER,
                amount REAL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(debt_id) REFERENCES debts(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info("Database initialized successfully with Babylon tables")

    def get_connection(self):
        """Возвращает соединение с базой данных"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
# Глобальный экземпляр для использования во всем приложении
db_connection = DatabaseConnection()