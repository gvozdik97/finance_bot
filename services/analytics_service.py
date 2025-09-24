# finance_bot/services/analytics_service.py

from datetime import datetime
from services.transaction_service import transaction_service

class AnalyticsService:
    def get_detailed_stats(self, user_id: int) -> dict:
        """Возвращает детальную статистику"""
        # За текущий месяц
        current_month = datetime.now().strftime('%Y-%m')
        
        # Получаем данные за текущий месяц
        monthly_transactions = transaction_service.get_user_transactions(user_id)
        monthly_summary = transaction_service.get_transactions_summary(user_id)
        
        # Получаем данные за все время
        all_time_transactions = transaction_service.get_user_transactions(user_id)
        all_time_summary = transaction_service.get_transactions_summary(user_id)
        
        # Статистика по категориям расходов
        expense_categories = {}
        for transaction in all_time_transactions:
            if transaction.type == 'expense':
                expense_categories[transaction.category] = expense_categories.get(transaction.category, 0) + transaction.amount
        
        # Сортируем по убыванию суммы
        top_expenses = dict(sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return {
            'monthly': {
                'income': monthly_summary['income'],
                'expense': monthly_summary['expense'],
                'margin': monthly_summary['margin']
            },
            'all_time': {
                'income': all_time_summary['income'],
                'expense': all_time_summary['expense'],
                'margin': all_time_summary['margin']
            },
            'top_expenses': top_expenses,
            'total_expenses': all_time_summary['expense']
        }

# Глобальный экземпляр сервиса
analytics_service = AnalyticsService()