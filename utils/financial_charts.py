# utils/financial_charts.py - ПРАКТИЧНЫЕ ТЕКСТОВЫЕ ГРАФИКИ

class FinancialCharts:
    """
    Создание простых и понятных текстовых графиков
    """
    
    @staticmethod
    def create_spending_by_category(categories_data: list, width: int = 20) -> str:
        """
        Создает текстовую диаграмму расходов по категориям
        """
        if not categories_data:
            return "📊 Нет данных о расходах за последний период"
        
        chart_text = "📊 *РАСХОДЫ ПО КАТЕГОРИЯМ:*\n\n"
        
        for category in categories_data[:8]:  # Ограничиваем 8 категориями
            name = category['name']
            percentage = category['percentage']
            amount = category['amount']
            
            # Создаем прогресс-бар
            bar_length = int(percentage / 100 * width)
            bar = '█' * bar_length + '░' * (width - bar_length)
            
            chart_text += f"{name}:\n"
            chart_text += f"{bar} {percentage:.1f}%\n"
            chart_text += f"Сумма: {amount:,.0f} руб.\n\n"
        
        return chart_text
    
    @staticmethod
    def create_income_vs_expenses(income: float, expenses: float, width: int = 20) -> str:
        """
        Создает сравнение доходов и расходов
        """
        if income <= 0:
            return "📈 Недостаточно данных для сравнения"
        
        ratio = expenses / income if income > 0 else 0
        savings = income - expenses
        
        chart_text = "📈 *ДОХОДЫ vs РАСХОДЫ:*\n\n"
        
        # Диаграмма доходов
        income_bar = '🟢' * width
        chart_text += f"Доходы: {income:,.0f} руб.\n{income_bar}\n\n"
        
        # Диаграмма расходов (относительно доходов)
        expense_ratio = min(1.0, ratio)
        expense_bar_length = int(expense_ratio * width)
        expense_bar = '🔴' * expense_bar_length + '⚪' * (width - expense_bar_length)
        
        chart_text += f"Расходы: {expenses:,.0f} руб. ({ratio*100:.1f}%)\n{expense_bar}\n\n"
        
        # Результат
        if savings > 0:
            savings_ratio = savings / income
            savings_bar_length = int(savings_ratio * width)
            savings_bar = '💰' * savings_bar_length + '⚪' * (width - savings_bar_length)
            chart_text += f"Накопления: +{savings:,.0f} руб.\n{savings_bar}"
        else:
            chart_text += f"⚠️ Перерасход: {abs(savings):,.0f} руб."
        
        return chart_text
    
    @staticmethod
    def create_monthly_trend(monthly_data: list) -> str:
        """
        Создает график месячной динамики
        """
        if not monthly_data:
            return "📅 Нет данных для построения графика"
        
        chart_text = "📅 *ДИНАМИКА ПО МЕСЯЦАМ:*\n\n"
        
        # Находим максимальное значение для масштабирования
        max_value = max([data[1] for data in monthly_data]) if monthly_data else 1
        
        for month, amount in monthly_data[:6]:  # Последние 6 месяцев
            # Упрощаем название месяца
            month_name = month[-2:]  # Берем только номер месяца
            
            # Создаем бар (масштабируем относительно максимума)
            bar_length = int((amount / max_value) * 15) if max_value > 0 else 0
            bar = '█' * bar_length
            
            chart_text += f"{month_name}. {amount:,.0f} руб. {bar}\n"
        
        return chart_text
    
    @staticmethod
    def create_savings_progress(gold_reserve: float, monthly_income: float) -> str:
        """
        Создает график прогресса накоплений
        """
        if monthly_income <= 0:
            return "💰 Добавьте данные о доходах для отслеживания накоплений"
        
        # Рассчитываем идеал (6 месяцев откладывания по 10%)
        ideal_savings = monthly_income * 0.1 * 6
        progress_ratio = min(1.0, gold_reserve / ideal_savings) if ideal_savings > 0 else 0
        
        chart_text = "💰 *ПРОГРЕСС НАКОПЛЕНИЙ:*\n\n"
        
        # Прогресс-бар
        bar_length = int(progress_ratio * 20)
        bar = '💰' * bar_length + '⚪' * (20 - bar_length)
        
        chart_text += f"Текущие накопления: {gold_reserve:,.0f} руб.\n"
        chart_text += f"Цель (6 месяцев): {ideal_savings:,.0f} руб.\n\n"
        chart_text += f"{bar} {progress_ratio*100:.1f}%\n\n"
        
        if progress_ratio >= 1.0:
            chart_text += "🎉 Отличный результат! Вы достигли цели!"
        elif progress_ratio >= 0.5:
            chart_text += "💪 Хороший прогресс! Продолжайте в том же духе!"
        else:
            chart_text += "🚀 Начните с малого - каждый доход откладывайте 10%"
        
        return chart_text

# Глобальный экземпляр
financial_charts = FinancialCharts()