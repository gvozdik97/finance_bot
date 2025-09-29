# services/user_settings_service.py - ОБНОВЛЕННАЯ ВЕРСИЯ
import logging
from typing import Dict, Optional
from database.connection import db_connection
from database.models import UserSettings

logger = logging.getLogger(__name__)

class UserSettingsService:
    """Сервис для управления пользовательскими настройками"""
    
    def init_user_settings(self, user_id: int) -> bool:
        """Инициализирует настройки для нового пользователя"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO user_settings (user_id, savings_rate, auto_savings)
                    VALUES (?, ?, ?)
                ''', (user_id, 10.0, True))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации настроек для пользователя {user_id}: {e}")
            return False
    
    def get_user_settings(self, user_id: int) -> Optional[UserSettings]:
        """Получает настройки пользователя"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, user_id, savings_rate, auto_savings, created_at, updated_at
                    FROM user_settings WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                
                if result:
                    return UserSettings(*result)
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения настроек для пользователя {user_id}: {e}")
            return None
    
    def update_savings_rate(self, user_id: int, savings_rate: float) -> bool:
        """Обновляет процент накоплений пользователя"""
        try:
            # Проверяем валидность процента
            if not (0 <= savings_rate <= 100):
                return False
            
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE user_settings 
                    SET savings_rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (savings_rate, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления процента накоплений для пользователя {user_id}: {e}")
            return False
    
    def toggle_auto_savings(self, user_id: int, auto_savings: bool) -> bool:
        """Включает/выключает автоматическое распределение доходов"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE user_settings 
                    SET auto_savings = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (auto_savings, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Ошибка переключения авто-накоплений для пользователя {user_id}: {e}")
            return False

# Глобальный экземпляр
user_settings_service = UserSettingsService()