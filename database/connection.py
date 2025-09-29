# database/connection.py - ПОЛНОСТЬЮ ПЕРЕПИСАННАЯ ВЕРСИЯ
import sqlite3
import logging
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, db_path='finance.db'):
        self.db_path = db_path
        self._lock = threading.RLock()
        self.init_db()
    
    def init_db(self):
        """Инициализирует таблицы базы данных"""
        with self.get_connection() as conn:
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
            
            # Таблица долгов
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
            
            # Таблица пользовательских настроек
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    savings_rate REAL DEFAULT 10.0,
                    auto_savings BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        
        logging.info("✅ База данных инициализирована успешно")
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для безопасной работы с базой данных"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            # Включаем WAL mode для лучшей параллельной работы
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=5000')
            conn.execute('PRAGMA foreign_keys=ON')
            
            yield conn
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

# Глобальный экземпляр
db_connection = DatabaseConnection()