# services/budget_planner.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database.connection import db_connection

logger = logging.getLogger(__name__)

class BudgetPlanner:
    """
    Расширенный сервис бюджетирования с аналитикой и рекомендациями
    """
    
    def check_existing_budget(self, user_id: int, category: str) -> Optional[float]:
        """Проверяет существование бюджета для категории"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT amount FROM budgets 
                    WHERE user_id = ? AND category = ? AND period = 'monthly'
                ''', (user_id, category))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Check existing budget error: {e}")
            return None
    
    def set_monthly_budget(self, user_id: int, category: str, amount: float) -> Dict:
        """Установка месячного бюджета по категории с проверкой дубликатов"""
        try:
            # Проверяем существующий бюджет
            existing_budget = self.check_existing_budget(user_id, category)
            
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                if existing_budget is not None:
                    # Обновляем существующий бюджет
                    cursor.execute('''
                        UPDATE budgets 
                        SET amount = ?, created_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND category = ? AND period = 'monthly'
                    ''', (amount, user_id, category))
                    
                    message = f"✅ *Бюджет обновлен!*\n\n" \
                             f"• Категория: {category}\n" \
                             f"• Старый лимит: {existing_budget:,.0f} руб.\n" \
                             f"• Новый лимит: {amount:,.0f} руб.\n\n" \
                             f"💡 Бюджет успешно перезаписан!"
                else:
                    # Создаем новый бюджет
                    cursor.execute('''
                        INSERT INTO budgets (user_id, category, amount, period)
                        VALUES (?, ?, ?, 'monthly')
                    ''', (user_id, category, amount))
                    
                    message = f"✅ *Бюджет установлен!*\n\n" \
                             f"• Категория: {category}\n" \
                             f"• Лимит в месяц: {amount:,.0f} руб.\n\n" \
                             f"💡 Теперь я буду следить за вашими расходами!"
                
                conn.commit()
                
                return {
                    'success': True,
                    'message': message,
                    'was_updated': existing_budget is not None
                }
                
        except Exception as e:
            logger.error(f"Budget set error: {e}")
            return {'success': False, 'error': 'Ошибка при установке бюджета'}
    
    def get_budget_progress(self, user_id: int) -> Dict:
        """Получает прогресс по всем бюджетам с аналитикой"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Получаем все установленные бюджеты
                cursor.execute('''
                    SELECT category, amount FROM budgets 
                    WHERE user_id = ? AND period = 'monthly'
                ''', (user_id,))
                budgets = cursor.fetchall()
                
                if not budgets:
                    return {
                        'success': True,
                        'has_budgets': False,
                        'message': "📊 У вас пока нет установленных бюджетов\n\n💡 Используйте '🎯 Установить бюджет' для начала планирования"
                    }
                
                # Рассчитываем прогресс по каждой категории
                budget_progress = []
                total_budget = 0
                total_spent = 0
                
                for category, budget_amount in budgets:
                    # Расходы по категории за текущий месяц
                    cursor.execute('''
                        SELECT COALESCE(SUM(amount), 0)
                        FROM transactions 
                        WHERE user_id = ? AND category = ? AND type = 'expense'
                        AND date >= date('now', 'start of month')
                    ''', (user_id, category))
                    
                    spent = cursor.fetchone()[0]
                    percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
                    remaining = max(0, budget_amount - spent)
                    
                    budget_progress.append({
                        'category': category,
                        'budget': budget_amount,
                        'spent': spent,
                        'remaining': remaining,
                        'percentage': percentage,
                        'status': self._get_budget_status(percentage)
                    })
                    
                    total_budget += budget_amount
                    total_spent += spent
                
                # Общая аналитика
                overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
                
                return {
                    'success': True,
                    'has_budgets': True,
                    'budgets': budget_progress,
                    'total_budget': total_budget,
                    'total_spent': total_spent,
                    'overall_percentage': overall_percentage,
                    'alerts': self._check_budget_alerts(budget_progress)
                }
                
        except Exception as e:
            logger.error(f"Budget progress error: {e}")
            return {'success': False, 'error': 'Ошибка при получении прогресса бюджетов'}
    
    def suggest_budgets(self, user_id: int) -> Dict:
        """Предлагает бюджеты на основе истории расходов"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                # Анализ средних расходов по категориям за последние 3 месяца
                cursor.execute('''
                    SELECT category, AVG(monthly_total) as avg_monthly
                    FROM (
                        SELECT category, strftime('%Y-%m', date) as month, 
                               SUM(amount) as monthly_total
                        FROM transactions 
                        WHERE user_id = ? AND type = 'expense'
                        AND date >= date('now', '-3 months')
                        GROUP BY category, month
                    )
                    GROUP BY category
                ''', (user_id,))
                
                spending_patterns = cursor.fetchall()
                
                if not spending_patterns:
                    return {
                        'success': True,
                        'has_suggestions': False,
                        'message': "📈 Недостаточно данных для рекомендаций\n\n💡 Добавьте несколько расходов для анализа"
                    }
                
                suggestions = []
                for category, avg_spending in spending_patterns:
                    # Предлагаем бюджет на 10-20% выше средних расходов
                    suggested_budget = avg_spending * 1.15
                    suggestions.append({
                        'category': category,
                        'avg_spending': avg_spending,
                        'suggested_budget': suggested_budget,
                        'reasoning': f"На основе средних расходов: {avg_spending:,.0f} руб./мес"
                    })
                
                return {
                    'success': True,
                    'has_suggestions': True,
                    'suggestions': suggestions
                }
                
        except Exception as e:
            logger.error(f"Budget suggestions error: {e}")
            return {'success': False, 'error': 'Ошибка при генерации рекомендаций'}
    
    def _get_budget_status(self, percentage: float) -> str:
        """Определяет статус бюджета на основе процента использования"""
        if percentage < 50:
            return "🟢 В норме"
        elif percentage < 80:
            return "🟡 Внимание"
        elif percentage < 100:
            return "🟠 Риск"
        else:
            return "🔴 Превышен"
    
    def _check_budget_alerts(self, budgets: List[Dict]) -> List[str]:
        """Проверяет бюджеты на превышение и генерирует уведомления"""
        alerts = []
        
        for budget in budgets:
            if budget['percentage'] >= 80:
                alert_msg = f"⚠️ {budget['category']}: использовано {budget['percentage']:.0f}%"
                if budget['percentage'] >= 100:
                    alert_msg += f" (превышение на {budget['spent'] - budget['budget']:,.0f} руб.)"
                alerts.append(alert_msg)
        
        return alerts
    
    def delete_budget(self, user_id: int, category: str) -> Dict:
        """Удаляет бюджет по категории"""
        try:
            with db_connection.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM budgets 
                    WHERE user_id = ? AND category = ? AND period = 'monthly'
                ''', (user_id, category))
                
                conn.commit()
                deleted = cursor.rowcount > 0
                
                if deleted:
                    return {
                        'success': True,
                        'message': f"🗑️ Бюджет для категории '{category}' удален"
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Бюджет для категории '{category}' не найден"
                    }
                    
        except Exception as e:
            logger.error(f"Budget delete error: {e}")
            return {'success': False, 'error': 'Ошибка при удалении бюджета'}

# Глобальный экземпляр
budget_planner = BudgetPlanner()