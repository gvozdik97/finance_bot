# services/transaction_editor.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database.connection import db_connection
from database.models import Transaction
from services.wallet_service import wallet_service

logger = logging.getLogger(__name__)

class TransactionEditor:
    """Сервис для редактирования существующих транзакций"""
    
    def get_recent_transactions_for_edit(self, user_id: int, limit: int = 5) -> List[Transaction]:
        """Получает последние транзакции для редактирования"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, user_id, type, amount, category, description, date
                    FROM transactions 
                    WHERE user_id = ? 
                    ORDER BY date DESC, id DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                transactions = []
                for row in cursor.fetchall():
                    transactions.append(Transaction(*row))
                
                return transactions
                
        except Exception as e:
            logger.error(f"Error getting transactions for edit: {e}")
            return []
    
    def get_transaction_by_id(self, user_id: int, transaction_id: int) -> Optional[Transaction]:
        """Получает транзакцию по ID"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, user_id, type, amount, category, description, date
                    FROM transactions 
                    WHERE id = ? AND user_id = ?
                ''', (transaction_id, user_id))
                
                result = cursor.fetchone()
                
                if result:
                    return Transaction(*result)
                return None
                
        except Exception as e:
            logger.error(f"Error getting transaction by ID: {e}")
            return None
    
    def edit_transaction(self, user_id: int, transaction_id: int, 
                        new_amount: float = None, new_category: str = None,
                        new_description: str = None) -> Dict:
        """Редактирует транзакцию с перерасчетом балансов"""
        try:
            # Получаем оригинальную транзакцию
            original_transaction = self.get_transaction_by_id(user_id, transaction_id)
            if not original_transaction:
                return {'success': False, 'error': 'Транзакция не найдена'}
            
            # Определяем изменения
            old_amount = original_transaction.amount
            new_amount = new_amount if new_amount is not None else old_amount
            new_category = new_category if new_category is not None else original_transaction.category
            new_description = new_description if new_description is not None else original_transaction.description
            
            # Если изменилась сумма, пересчитываем балансы
            if old_amount != new_amount:
                self._recalculate_balances(user_id, original_transaction, old_amount, new_amount)
            
            # Обновляем транзакцию в базе
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE transactions 
                    SET amount = ?, category = ?, description = ?, date = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                ''', (new_amount, new_category, new_description, transaction_id, user_id))
                
                conn.commit()
            
            return {
                'success': True,
                'message': self._get_edit_success_message(original_transaction, new_amount, new_category),
                'changes': {
                    'amount_changed': old_amount != new_amount,
                    'old_amount': old_amount,
                    'new_amount': new_amount
                }
            }
            
        except Exception as e:
            logger.error(f"Error editing transaction: {e}")
            return {'success': False, 'error': 'Ошибка при редактировании транзакции'}
    
    def _recalculate_balances(self, user_id: int, transaction: Transaction, 
                            old_amount: float, new_amount: float):
        """Пересчитывает балансы после изменения суммы транзакции"""
        amount_diff = new_amount - old_amount
        
        if transaction.type == 'income':
            # Для доходов: пересчитываем распределение
            from services.user_settings_service import user_settings_service
            settings = user_settings_service.get_user_settings(user_id)
            savings_rate = settings.savings_rate if settings else 10.0
            
            gold_reserve_diff = round(amount_diff * (savings_rate / 100), 2)
            living_budget_diff = amount_diff - gold_reserve_diff
            
            wallet_service.update_wallet_balance(user_id, 'gold_reserve', gold_reserve_diff)
            wallet_service.update_wallet_balance(user_id, 'living_budget', living_budget_diff)
            
        else:  # expense
            # Для расходов: просто корректируем бюджет на жизнь
            wallet_service.update_wallet_balance(user_id, 'living_budget', -amount_diff)
    
    def _get_edit_success_message(self, transaction: Transaction, 
                                new_amount: float, new_category: str) -> str:
        """Генерирует сообщение об успешном редактировании"""
        emoji = "💳" if transaction.type == 'income' else "💸"
        type_text = "доход" if transaction.type == 'income' else "расход"
        
        return (f"✅ *Транзакция отредактирована!*\n\n"
                f"{emoji} *{type_text.capitalize()}*\n"
                f"• Сумма: {new_amount:,.0f} руб.\n"
                f"• Категория: {new_category}\n"
                f"• Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                f"💡 Балансы автоматически пересчитаны")
    
    def delete_transaction(self, user_id: int, transaction_id: int) -> Dict:
        """Удаляет транзакцию с перерасчетом балансов"""
        try:
            transaction = self.get_transaction_by_id(user_id, transaction_id)
            if not transaction:
                return {'success': False, 'error': 'Транзакция не найдена'}
            
            # Отменяем влияние транзакции на балансы
            if transaction.type == 'income':
                # Для доходов: вычитаем из балансов
                from services.user_settings_service import user_settings_service
                settings = user_settings_service.get_user_settings(user_id)
                savings_rate = settings.savings_rate if settings else 10.0
                
                gold_reserve_revert = -round(transaction.amount * (savings_rate / 100), 2)
                living_budget_revert = -(transaction.amount - abs(gold_reserve_revert))
                
                wallet_service.update_wallet_balance(user_id, 'gold_reserve', gold_reserve_revert)
                wallet_service.update_wallet_balance(user_id, 'living_budget', living_budget_revert)
                
            else:  # expense
                # Для расходов: возвращаем сумму в бюджет
                wallet_service.update_wallet_balance(user_id, 'living_budget', transaction.amount)
            
            # Удаляем транзакцию
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM transactions 
                    WHERE id = ? AND user_id = ?
                ''', (transaction_id, user_id))
                
                conn.commit()
            
            return {
                'success': True,
                'message': f"🗑️ *Транзакция удалена!*\n\nБалансы автоматически пересчитаны"
            }
            
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            return {'success': False, 'error': 'Ошибка при удалении транзакции'}

# Глобальный экземпляр
transaction_editor = TransactionEditor()