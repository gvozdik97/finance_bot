# services/debt_service.py - РАСШИРЕННАЯ ВЕРСИЯ С ИНТЕГРАЦИЕЙ БЮДЖЕТА

import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database.connection import db_connection
from database.models import Debt
from services.wallet_service import wallet_service  # ✅ ДОБАВИЛИ ИМПОРТ

logger = logging.getLogger(__name__)

class DebtService:
    """
    Чистая вавилонская система управления долгами с интеграцией в бюджет 90%.
    """
    
    def __init__(self):
        self.conn = db_connection
    
    def add_debt(self, user_id: int, creditor: str, amount: float, 
                interest_rate: float = 0.0, due_date: Optional[datetime] = None) -> Dict:
        """Добавляет новый долг с вавилонской мудростью"""
        # Без изменений (предыдущая реализация)
        try:
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO debts (user_id, creditor, initial_amount, current_amount, 
                                 interest_rate, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, creditor, amount, amount, interest_rate, due_date, 'active'))
            
            conn.commit()
            debt_id = cursor.lastrowid
            conn.close()
            
            wisdom = self._get_debt_wisdom_message(amount, creditor)
            
            return {
                'success': True,
                'debt_id': debt_id,
                'message': f"🏛️ *Долг добавлен!*\n\n"
                          f"• Кредитор: {creditor}\n"
                          f"• Сумма: {amount:,.0f} руб.\n"
                          f"• Ставка: {interest_rate}%\n\n"
                          f"{wisdom}"
            }
            
        except Exception as e:
            logger.error(f"Debt add error: {e}")
            return {'success': False, 'error': 'Ошибка при добавлении долга'}
    
    def make_payment(self, user_id: int, debt_id: int, amount: float) -> Dict:
        """
        Погашение долга с ПРОВЕРКОЙ БЮДЖЕТА 90% и списанием средств
        """
        try:
            # 🔒 ВАВИЛОНСКОЕ ПРАВИЛО: погашение только из Бюджета на жизнь (90%)
            affordability = wallet_service.can_afford_expense(user_id, amount)
            
            if not affordability['can_afford']:
                return {
                    'success': False,
                    'error': f"🚫 *Недостаточно средств в Бюджете на жизнь!*\n\n"
                            f"💼 Доступно: {affordability['available']:,.0f} руб.\n"
                            f"💸 Нужно для погашения: {amount:,.0f} руб.\n"
                            f"📉 Не хватает: {affordability['shortfall']:,.0f} руб.\n\n"
                            f"💡 *Мудрость Вавилона:* «Сначала накопить, потом погашать»"
                }
            
            conn = self.conn.get_connection()
            cursor = conn.cursor()
            
            # Получаем информацию о долге
            cursor.execute('''
                SELECT current_amount, creditor FROM debts 
                WHERE id = ? AND user_id = ? AND status = 'active'
            ''', (debt_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': 'Долг не найден'}
            
            current_amount, creditor = result
            
            if amount > current_amount:
                amount = current_amount  # Нельзя заплатить больше долга
            
            new_amount = current_amount - amount
            status = 'paid' if new_amount <= 0 else 'active'
            
            # 🔒 ВАВИЛОНСКОЕ ПРАВИЛО: списание из Бюджета на жизнь
            wallet_service.update_wallet_balance(user_id, 'living_budget', -amount)
            
            # Обновляем долг
            cursor.execute('''
                UPDATE debts 
                SET current_amount = ?, status = ?
                WHERE id = ? AND user_id = ?
            ''', (new_amount, status, debt_id, user_id))
            
            # Сохраняем запись о погашении (для истории)
            cursor.execute('''
                INSERT INTO debt_payments (user_id, debt_id, amount, payment_date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, debt_id, amount))
            
            conn.commit()
            conn.close()
            
            # Обновляем прогресс правила "Свобода от долгов"
            self._update_debt_rule_progress(user_id)
            
            wisdom = self._get_payment_wisdom_message(amount, creditor, status)
            new_budget_balance = affordability['available'] - amount
            
            return {
                'success': True,
                'message': f"🎉 *Платеж по долгу выполнен!*\n\n"
                          f"• Кредитор: {creditor}\n"
                          f"• Сумма платежа: {amount:,.0f} руб.\n"
                          f"• Остаток долга: {new_amount:,.0f} руб.\n"
                          f"• Статус: {'✅ Погашен' if status == 'paid' else '📋 Активен'}\n"
                          f"• 💼 Новый баланс бюджета: {new_budget_balance:,.0f} руб.\n\n"
                          f"{wisdom}"
            }
            
        except Exception as e:
            logger.error(f"Debt payment error: {e}")
            return {'success': False, 'error': 'Ошибка при погашении долга'}
    
    def get_debt_statistics(self, user_id: int) -> Dict:
        """
        Возвращает статистику по долгам с вавилонской аналитикой
        """
        debts = self.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        
        # Получаем баланс бюджета для анализа
        budget_balance = wallet_service.get_wallet_balance(user_id, 'living_budget')
        
        # Рассчитываем вавилонские метрики
        debt_to_budget_ratio = (total_debt / budget_balance * 100) if budget_balance > 0 else float('inf')
        
        # Рекомендации на основе метрик
        if total_debt == 0:
            recommendation = "🎉 Идеально! Вы свободны от долгового бремени."
            risk_level = "🟢 Низкий"
        elif debt_to_budget_ratio < 50:
            recommendation = "💪 Хорошо! Долговая нагрузка умеренная."
            risk_level = "🟡 Средний"
        elif debt_to_budget_ratio < 100:
            recommendation = "⚠️ Внимание! Высокая долговая нагрузка."
            risk_level = "🟠 Высокий"
        else:
            recommendation = "🚨 Критично! Долги превышают доступный бюджет."
            risk_level = "🔴 Критический"
        
        return {
            'total_debt': total_debt,
            'debt_count': len(debts),
            'budget_balance': budget_balance,
            'debt_to_budget_ratio': debt_to_budget_ratio,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'estimated_payoff_time': self._estimate_payoff_time(user_id, total_debt)
        }
    
    def _estimate_payoff_time(self, user_id: int, total_debt: float) -> str:
        """
        Оценивает время погашения долгов на основе типичных платежей
        """
        if total_debt == 0:
            return "Долгов нет"
        
        # Средний платеж (5% от долга или 1000 руб., что больше)
        avg_payment = max(1000, total_debt * 0.05)
        months = total_debt / avg_payment
        
        if months < 1:
            return "менее 1 месяца"
        elif months < 12:
            return f"около {int(months)} месяцев"
        else:
            years = months / 12
            return f"около {years:.1f} лет"
    
    def _update_debt_rule_progress(self, user_id: int):
        """Обновляет прогресс правила 'Свобода от долгов'"""
        debts = self.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        
        # Прогресс: 100% если долгов нет, уменьшается с ростом долга
        if total_debt == 0:
            progress = 100.0
        else:
            # Чем меньше долг, тем выше прогресс (логарифмическая шкала)
            progress = max(0.0, min(100.0, (1 - (total_debt / (total_debt + 50000))) * 100))
        
        from services.babylon_service import babylon_service
        babylon_service.update_rule_progress(user_id, 'debt_free', progress)
    
    def get_recommended_payment_amount(self, user_id: int) -> float:
        """
        Рекомендует сумму платежа на основе доступного бюджета
        """
        budget_balance = wallet_service.get_wallet_balance(user_id, 'living_budget')
        debts = self.get_active_debts(user_id)
        
        if not debts or budget_balance <= 0:
            return 0.0
        
        # Рекомендуем 10-20% от доступного бюджета, но не менее 1000 руб.
        recommended = min(budget_balance * 0.2, budget_balance * 0.1)
        return max(1000.0, recommended)
    
    # Остальные методы без изменений...
    def get_active_debts(self, user_id: int) -> List[Debt]:
        """Возвращает список активных долгов пользователя"""
        conn = self.conn.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, creditor, initial_amount, current_amount, 
                   interest_rate, due_date, status, created_at
            FROM debts 
            WHERE user_id = ? AND status = 'active'
            ORDER BY current_amount DESC
        ''', (user_id,))
        
        debts = []
        for row in cursor.fetchall():
            debts.append(Debt(*row))
        
        conn.close()
        return debts
    
    def calculate_snowball_plan(self, user_id: int) -> Dict:
        """Рассчитывает план погашения по методу 'снежного кома'"""
        debts = self.get_active_debts(user_id)
        
        if not debts:
            return {'has_debts': False, 'message': '🎉 У вас нет активных долгов!'}
        
        sorted_debts = sorted(debts, key=lambda x: x.current_amount)
        
        plan = []
        total_debt = sum(debt.current_amount for debt in debts)
        
        for i, debt in enumerate(sorted_debts):
            plan.append({
                'priority': i + 1,
                'creditor': debt.creditor,
                'amount': debt.current_amount,
                'recommended_payment': self._calculate_recommended_payment(debt)
            })
        
        return {
            'has_debts': True,
            'total_debt': total_debt,
            'plan': plan,
            'message': self._get_snowball_wisdom_message(total_debt, len(debts))
        }
    
    def _calculate_recommended_payment(self, debt: Debt) -> float:
        """Рассчитывает рекомендуемый платеж на основе суммы долга"""
        base_payment = 1000
        percentage = 0.05
        return max(base_payment, debt.current_amount * percentage)
    
    def _get_debt_wisdom_message(self, amount: float, creditor: str) -> str:
        """Возвращает вавилонскую мудрость при добавлении долга"""
        wisdoms = [
            f"«Долг — это господин, который делает свободного человека рабом»",
            f"«Мудрый человек избегает долгов, как корабль избегает скал»",
            f"«Путь к богатству начинается с освобождения от долгов»"
        ]
        import random
        return f"💡 *Мудрость Вавилона:* {random.choice(wisdoms)}"
    
    def _get_payment_wisdom_message(self, amount: float, creditor: str, status: str) -> str:
        """Возвращает мудрость при погашении долга"""
        if status == 'paid':
            return "🎊 *Поздравляем!* Вы освободились от одного из долговых оков!"
        else:
            return "💪 *Продолжайте в том же духе!* Каждый платеж приближает вас к финансовой свободе."
    
    def _get_snowball_wisdom_message(self, total_debt: float, num_debts: int) -> str:
        """Возвращает мудрость для плана погашения"""
        return f"🏛️ *Совет Вавилона:* «Погашайте малые долги первыми — это даст силы для больших побед!»"

    def get_debt_freedom_timeline(self, user_id: int) -> Dict:
        """
        Возвращает временную шкалу освобождения от долгов
        """
        debts = self.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        
        if total_debt == 0:
            return {
                'is_free': True,
                'message': '🎉 Вы уже свободны от долгов!',
                'timeline': []
            }
        
        # Рассчитываем предполагаемые даты погашения
        monthly_payment = self.get_recommended_payment_amount(user_id)
        timeline = []
        
        current_date = datetime.now()
        remaining_debt = total_debt
        
        for i in range(12):  # На 12 месяцев вперед
            if remaining_debt <= 0:
                break
            
            payment_date = current_date + timedelta(days=30 * (i + 1))
            payment_amount = min(monthly_payment, remaining_debt)
            remaining_debt -= payment_amount
            
            timeline.append({
                'month': i + 1,
                'date': payment_date.strftime('%d.%m.%Y'),
                'payment': payment_amount,
                'remaining': remaining_debt,
                'progress': ((total_debt - remaining_debt) / total_debt * 100) if total_debt > 0 else 100
            })
        
        return {
            'is_free': False,
            'total_debt': total_debt,
            'monthly_payment': monthly_payment,
            'estimated_months': len(timeline),
            'timeline': timeline
        }
    
    def get_motivational_message(self, user_id: int) -> str:
        """
        Возвращает мотивационное сообщение на основе прогресса
        """
        debts = self.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        initial_debt = sum(debt.initial_amount for debt in debts)
        
        if total_debt == 0:
            return random.choice([
                "🎊 *Поздравляем!* Вы достигли финансовой свободы!",
                "🏛️ *Мудрость Вавилона:* «Свободный человек — богатый человек!»",
                "💎 Теперь ваши деньги работают на вас, а не вы на долги!"
            ])
        
        progress = ((initial_debt - total_debt) / initial_debt * 100) if initial_debt > 0 else 0
        
        if progress < 25:
            messages = [
                "💪 *Начало пути!* Помните: каждый большой путь начинается с маленького шага.",
                "🎯 *Совет Вавилона:* «Регулярность — ключ к успеху в погашении долгов.»",
                "⛓️ *Первые шаги* самые важные. Не сдавайтесь!"
            ]
        elif progress < 50:
            messages = [
                "🚀 *Отличный прогресс!* Вы уже прошли значительную часть пути.",
                "🔓 *Совет Вавилона:* «Маленькие долги исчезают быстро — это придает сил!»",
                "📈 *Половина пути пройдена!* Теперь вы видите свет в конце тоннеля."
            ]
        elif progress < 75:
            messages = [
                "🏃 *Финальный рывок!* Осталось совсем немного до полной свободы.",
                "💎 *Совет Вавилона:* «Не сбавляйте темп на финишной прямой!»",
                "✨ *Почти у цели!* Ваша финансовая свобода близка."
            ]
        else:
            messages = [
                "🎊 *Финальные метры!* Вы на пороге финансовой свободы!",
                "🏛️ *Совет Вавилона:* «Последние усилия самые важные!»",
                "🚪 *Дверь к свободе* уже приоткрыта. Остался последний шаг!"
            ]
        
        return random.choice(messages)

# Глобальный экземпляр сервиса
debt_service = DebtService()