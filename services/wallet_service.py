# services/wallet_service.py - ОБНОВЛЕННАЯ ВЕРСИЯ
import logging
from typing import Dict, List, Optional
from database.connection import db_connection
from database.models import Wallet

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self):
        self.wallet_types = ['gold_reserve', 'living_budget', 'debt_repayment']
    
    def init_user_wallets(self, user_id: int) -> bool:
        """Инициализирует три кошелька для нового пользователя"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                for wallet_type in self.wallet_types:
                    cursor.execute('''
                        INSERT OR IGNORE INTO wallets (user_id, wallet_type, balance)
                        VALUES (?, ?, ?)
                    ''', (user_id, wallet_type, 0.0))
                
                conn.commit()
            
            # Инициализируем настройки пользователя
            from .user_settings_service import user_settings_service
            user_settings_service.init_user_settings(user_id)
            
            # Инициализируем правила Вавилона
            from .babylon_service import babylon_service
            babylon_service.init_user_rules(user_id)
            
            logger.info(f"✅ Инициализированы кошельки для пользователя {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации кошельков для пользователя {user_id}: {e}")
            return False
    
    def distribute_income(self, user_id: int, amount: float) -> Dict:
        """Распределяет доход по правилу 10%/90%"""
        try:
            gold_reserve = round(amount * 0.10, 2)
            living_budget = round(amount * 0.90, 2)
            
            # Обновляем балансы кошельков
            self.update_wallet_balance(user_id, 'gold_reserve', gold_reserve)
            self.update_wallet_balance(user_id, 'living_budget', living_budget)
            
            return {
                'success': True,
                'gold_reserve': gold_reserve,
                'living_budget': living_budget,
                'total_income': amount,
                'message': f"🏦 *Распределение по правилам Вавилона:*\n\n"
                          f"💰 *Золотой запас (10%):* {gold_reserve:,.0f} руб.\n"
                          f"💼 *Бюджет на жизнь (90%):* {living_budget:,.0f} руб.\n"
                          f"📊 *Общий доход:* {amount:,.0f} руб."
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка распределения дохода для пользователя {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def distribute_income_flexible(self, user_id: int, amount: float, use_custom_settings: bool = True) -> Dict:
        """Распределяет доход с учетом пользовательских настроек"""
        try:
            from .user_settings_service import user_settings_service
            
            if use_custom_settings:
                settings = user_settings_service.get_user_settings(user_id)
                if settings and settings.auto_savings:
                    savings_rate = settings.savings_rate
                else:
                    savings_rate = 0  # Если авто-накопления выключены
            else:
                savings_rate = 10.0  # Стандартное правило 10%
            
            gold_reserve = round(amount * (savings_rate / 100), 2)
            living_budget = round(amount - gold_reserve, 2)
            
            # Обновляем балансы кошельков
            self.update_wallet_balance(user_id, 'gold_reserve', gold_reserve)
            self.update_wallet_balance(user_id, 'living_budget', living_budget)
            
            return {
                'success': True,
                'gold_reserve': gold_reserve,
                'living_budget': living_budget,
                'savings_rate': savings_rate,
                'total_income': amount,
                'message': self._get_distribution_message(amount, gold_reserve, living_budget, savings_rate)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка гибкого распределения для пользователя {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_wallet_balance(self, user_id: int, wallet_type: str, amount: float) -> bool:
        """Обновляет баланс кошелька"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE wallets 
                    SET balance = balance + ?, created_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND wallet_type = ?
                ''', (amount, user_id, wallet_type))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления баланса кошелька: {e}")
            return False
    
    def get_wallet_balance(self, user_id: int, wallet_type: str) -> float:
        """Возвращает баланс конкретного кошелька"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT balance FROM wallets 
                    WHERE user_id = ? AND wallet_type = ?
                ''', (user_id, wallet_type))
                
                result = cursor.fetchone()
                return result[0] if result else 0.0
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения баланса кошелька: {e}")
            return 0.0
    
    def get_all_wallets(self, user_id: int) -> Dict[str, float]:
        """Возвращает балансы всех кошельков пользователя"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT wallet_type, balance FROM wallets 
                    WHERE user_id = ?
                ''', (user_id,))
                
                wallets = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Гарантируем, что все типы кошельков присутствуют
                for wallet_type in self.wallet_types:
                    if wallet_type not in wallets:
                        wallets[wallet_type] = 0.0
                
                return wallets
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения всех кошельков: {e}")
            return {wallet_type: 0.0 for wallet_type in self.wallet_types}
    
    def get_wallet_display_name(self, wallet_type: str) -> str:
        """Возвращает читаемое название кошелька"""
        names = {
            'gold_reserve': '💰 Золотой запас (10%)',
            'living_budget': '💼 Бюджет на жизнь (90%)',
            'debt_repayment': '🏛️ Фонд погашения долгов'
        }
        return names.get(wallet_type, wallet_type)
    
    def can_afford_expense(self, user_id: int, amount: float) -> Dict:
        """Проверяет, достаточно ли средств в бюджете на жизнь для расхода"""
        living_budget = self.get_wallet_balance(user_id, 'living_budget')
        
        return {
            'can_afford': living_budget >= amount,
            'available': living_budget,
            'needed': amount,
            'shortfall': max(0, amount - living_budget)
        }
    
    def _get_distribution_message(self, amount: float, gold_reserve: float, 
                                living_budget: float, savings_rate: float) -> str:
        """Генерирует сообщение о распределении доходов"""
        if savings_rate > 0:
            return (f"🏦 *Распределение дохода ({savings_rate}%)*\n\n"
                    f"💰 *Золотой запас ({savings_rate}%):* {gold_reserve:,.0f} руб.\n"
                    f"💼 *Бюджет на жизнь ({100-savings_rate}%):* {living_budget:,.0f} руб.\n"
                    f"📊 *Общий доход:* {amount:,.0f} руб.")
        else:
            return (f"🏦 *Доход добавлен в бюджет*\n\n"
                    f"💼 *Бюджет на жизнь:* {amount:,.0f} руб.\n"
                    f"💡 *Накопления отключены*")

# Глобальный экземпляр сервиса
wallet_service = WalletService()