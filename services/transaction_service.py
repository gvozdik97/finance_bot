# services/transaction_service.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import logging
from typing import Dict
from database.connection import db_connection
from services.wallet_service import wallet_service  # ← ДОБАВЛЯЕМ ИМПОРТ

logger = logging.getLogger(__name__)

class TransactionService:
    """
    Чистый вавилонский сервис транзакций.
    Только правила 10%/90%, никакого общего учета.
    """
    
    def __init__(self):
        pass  # Убираем self.conn, используем глобальный db_connection
    
    def add_income(self, user_id: int, amount: float, category: str, description: str = "", 
                   use_custom_settings: bool = True) -> Dict:
        """
        Добавляет доход с ГИБКИМ распределением
        """
        try:
            # Гибкое распределение дохода
            distribution = wallet_service.distribute_income_flexible(
                user_id, amount, use_custom_settings
            )
            
            if not distribution['success']:
                return distribution
            
            # Сохраняем запись о доходе (для истории)
            self._save_transaction(user_id, 'income', amount, category, description)
            
            return {
                'success': True,
                'message': distribution['message'],
                'distribution': {
                    'gold_reserve': distribution['gold_reserve'],
                    'living_budget': distribution['living_budget'],
                    'savings_rate': distribution['savings_rate']
                }
            }
            
        except Exception as e:
            logger.error(f"Income error for user {user_id}: {e}")
            return {'success': False, 'error': 'Ошибка при добавлении дохода'}
    
    def add_expense(self, user_id: int, amount: float, category: str, description: str = "") -> Dict:
        """
        Добавляет расход ТОЛЬКО из Бюджета на жизнь (90%)
        """
        try:
            # ВАВИЛОНСКОЕ ПРАВИЛО: расходы только из 90%
            affordability = wallet_service.can_afford_expense(user_id, amount)
            
            if not affordability['can_afford']:
                return {
                    'success': False,
                    'error': f"🚫 *Недостаточно средств в Бюджете на жизнь!*\n\n"
                            f"💼 Доступно: {affordability['available']:,.0f} руб.\n"
                            f"💸 Нужно: {affordability['needed']:,.0f} руб.\n"
                            f"📉 Не хватает: {affordability['shortfall']:,.0f} руб."
                }
            
            # Списание ТОЛЬКО из Бюджета на жизнь
            wallet_service.update_wallet_balance(user_id, 'living_budget', -amount)
            
            # Сохраняем запись о расходе
            self._save_transaction(user_id, 'expense', amount, category, description)
            
            new_balance = affordability['available'] - amount
            
            return {
                'success': True,
                'message': f"💸 *Расход выполнен из Бюджета на жизнь!*\n\n"
                          f"• Сумма: {amount:,.0f} руб.\n"
                          f"• Категория: {category}\n"
                          f"• Остаток: {new_balance:,.0f} руб.",
                'new_balance': new_balance
            }
            
        except Exception as e:
            logger.error(f"Expense error for user {user_id}: {e}")
            return {'success': False, 'error': 'Ошибка при добавлении расхода'}
    
    def _save_transaction(self, user_id: int, transaction_type: str, amount: float, 
                         category: str, description: str):
        """Внутренний метод для сохранения транзакции в историю"""
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (user_id, type, amount, category, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, transaction_type, amount, category, description))
            
            conn.commit()
    
    def get_transaction_history(self, user_id: int, limit: int = 10) -> list:
        """Простая история транзакций (только для отображения)"""
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT type, amount, category, description, date 
                FROM transactions 
                WHERE user_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            transactions = cursor.fetchall()
            return transactions

# Глобальный экземпляр ЧИСТОГО сервиса
transaction_service = TransactionService()