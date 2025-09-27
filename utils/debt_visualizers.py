# utils/debt_visualizers.py - БАЗОВАЯ ВЕРСИЯ

import random
from services.debt_service import debt_service

class DebtVisualizer:
    """Визуализация прогресса освобождения от долгов"""
    
    @staticmethod
    def create_debt_freedom_progress(user_id: int) -> str:
        """Создает визуализацию прогресса освобождения от долгов"""
        debts = debt_service.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        
        if total_debt == 0:
            return "🎉 *Поздравляем! Вы свободны от долгов!* 🎉"
        
        initial_debt = sum(debt.initial_amount for debt in debts)
        progress = ((initial_debt - total_debt) / initial_debt * 100) if initial_debt > 0 else 0
        
        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        
        return f"""
📈 *Прогресс освобождения от долгов*

{progress_bar} {progress:.1f}%

💰 Начальная сумма: {initial_debt:,.0f} руб.
🎯 Текущий долг: {total_debt:,.0f} руб.
✅ Погашено: {initial_debt - total_debt:,.0f} руб.

💡 *Совет Вавилона:* «Каждый платеж приближает вас к финансовой свободе!»
"""
    
    @staticmethod
    def create_debt_milestones(user_id: int) -> str:
        """Создает визуализацию достижений в погашении долгов"""
        debts = debt_service.get_active_debts(user_id)
        total_debt = sum(debt.current_amount for debt in debts)
        initial_debt = sum(debt.initial_amount for debt in debts)
        
        if total_debt == 0:
            return "🏆 *Поздравляем! Вы достигли полной финансовой свободы!*"
        
        progress = ((initial_debt - total_debt) / initial_debt * 100) if initial_debt > 0 else 0
        
        milestones_text = "🎯 *Вехи освобождения от долгов*\n\n"
        
        milestones = [
            (25, "🥉 Бронзовый уровень", "Первый серьезный прогресс!"),
            (50, "🥈 Серебряный уровень", "Половина пути пройдена!"),
            (75, "🥇 Золотой уровень", "Осталось совсем немного!"),
            (100, "🏆 Полная свобода", "Вы достигли финансовой свободы!")
        ]
        
        for threshold, title, description in milestones:
            if progress >= threshold:
                status = "✅ ДОСТИГНУТО"
            else:
                status = "⏳ В ПРОЦЕССЕ"
            
            milestones_text += f"{title} - {status}\n"
            milestones_text += f"   {description}\n\n"
        
        milestones_text += f"📊 Текущий прогресс: {progress:.1f}%"
        
        return milestones_text