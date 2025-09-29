# services/babylon_service.py - ОБНОВЛЕННАЯ ВЕРСИЯ
import logging
import random
from typing import Dict
from database.connection import db_connection

logger = logging.getLogger(__name__)

class BabylonService:
    def __init__(self):
        self.rules = {
            '10_percent_rule': {
                'name': 'Правило 10%',
                'description': 'Откладывать 10% от каждого дохода в Золотой запас',
                'emoji': '💰'
            },
            'control_expenses': {
                'name': 'Контроль расходов', 
                'description': 'Тратить только из Бюджета на жизнь (90%)',
                'emoji': '💼'
            },
            'debt_free': {
                'name': 'Свобода от долгов',
                'description': 'Регулярно направлять средства на погашение долгов',
                'emoji': '🏛️'
            },
            'wise_investment': {
                'name': 'Мудрые инвестиции',
                'description': 'Заставлять деньги работать и приносить новый доход',
                'emoji': '📈'
            }
        }
    
    def init_user_rules(self, user_id: int) -> bool:
        """Инициализирует прогресс правил для нового пользователя"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                for rule_name in self.rules.keys():
                    cursor.execute('''
                        INSERT OR IGNORE INTO babylon_rules (user_id, rule_name, progress)
                        VALUES (?, ?, ?)
                    ''', (user_id, rule_name, 0.0))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации правил для пользователя {user_id}: {e}")
            return False
    
    def get_daily_quote(self) -> str:
        """Возвращает случайную цитату из книги"""
        quotes = [
            "«Часть того, что ты зарабатываешь, должна остаться у тебя»",
            "«Богатство — это сила. Сохраняй хотя бы десятую часть заработка»",
            "«Золото охотнее приходит к человеку, который откладывает десятую часть»",
            "«Расходы всегда растут до уровня доходов, если не контролировать их»",
            "«Сначала заплати себе — это основа финансовой свободы»",
            "«Каждая монета, которая уходит на ненужные траты, — это потерянное будущее богатство»"
        ]
        return random.choice(quotes)
    
    def get_welcome_message(self) -> str:
        """Возвращает приветственное сообщение с цитатой"""
        quote = self.get_daily_quote()
        return f"""🏛️ *Добро пожаловать в Финансовый Вавилон!*

{quote}

*7 Правил Богатства из Древнего Вавилона:*
1. 💰 Начинай сберегать — откладывай 10% от каждого дохода
2. 💼 Контролируй расходы — живи на 90% от заработка  
3. 📈 Приумножай деньги — заставь сбережения работать
4. 🛡️ Оберегай богатство — избегай рисковых вложений
5. 🏠 Делай дом выгодным вложением
6. 🧓 Обеспечь будущий доход
7. 🎯 Повышай свою квалификацию

*Готов следовать мудрости древних?*"""
    
    def update_rule_progress(self, user_id: int, rule_name: str, progress: float) -> bool:
        """Обновляет прогресс выполнения правила"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE babylon_rules 
                    SET progress = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND rule_name = ?
                ''', (progress, user_id, rule_name))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления прогресса правила: {e}")
            return False
    
    def get_user_progress(self, user_id: int) -> Dict:
        """Возвращает прогресс пользователя по всем правилам"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT rule_name, progress FROM babylon_rules 
                    WHERE user_id = ?
                ''', (user_id,))
                
                progress = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Гарантируем, что все правила присутствуют
                for rule_name in self.rules.keys():
                    if rule_name not in progress:
                        progress[rule_name] = 0.0
                
                return progress
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения прогресса пользователя: {e}")
            return {rule_name: 0.0 for rule_name in self.rules.keys()}

# Глобальный экземпляр сервиса
babylon_service = BabylonService()