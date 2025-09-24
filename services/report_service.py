# finance_bot/services/report_service.py

import io
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from services.transaction_service import transaction_service

class ReportService:
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """Настраивает стили графиков"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def get_period_data(self, period_type: str) -> tuple:
        """Возвращает даты начала и конца периода"""
        now = datetime.now()
        
        if period_type == 'current':
            start_date = now.replace(day=1)
            end_date = now
            period_name = "текущий месяц"
        elif period_type == 'previous':
            end_date = now.replace(day=1) - timedelta(days=1)
            start_date = end_date.replace(day=1)
            period_name = "прошлый месяц"
        else:
            days = int(period_type)
            end_date = now
            start_date = end_date - timedelta(days=days)
            
            if days == 7:
                period_name = "неделю"
            elif days == 30:
                period_name = "месяц"
            elif days == 90:
                period_name = "квартал"
            else:
                period_name = "год"
        
        return start_date, end_date, period_name
    
    def generate_report(self, user_id: int, period_type: str) -> dict:
        """Генерирует отчет с графиками и статистикой"""
        try:
            start_date, end_date, period_name = self.get_period_data(period_type)
            
            # Получаем данные
            transactions = transaction_service.get_user_transactions(
                user_id, start_date=start_date, end_date=end_date
            )
            
            if not transactions:
                return {'success': False, 'error': f"Нет данных за {period_name}."}
            
            # Создаем DataFrame для анализа
            df = pd.DataFrame([(t.type, t.amount, t.category, t.date) for t in transactions],
                            columns=['type', 'amount', 'category', 'date'])
            
            # Создаем график
            image_buffer = self.create_report_chart(df)
            
            # Генерируем текст отчета
            report_text = self.generate_report_text(df, period_name)
            
            return {
                'success': True,
                'image_buffer': image_buffer,
                'report_text': report_text,
                'period_name': period_name
            }
            
        except Exception as e:
            logging.error(f"Report generation error: {e}")
            return {'success': False, 'error': "Ошибка при создании отчета."}
    
    def create_report_chart(self, df: pd.DataFrame) -> io.BytesIO:
        """Создает график отчета"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Круговая диаграмма расходов
        expenses = df[df['type'] == 'expense']
        if not expenses.empty:
            expense_by_category = expenses.groupby('category')['amount'].sum()
            ax1.pie(expense_by_category.values, labels=expense_by_category.index, autopct='%1.1f%%')
            ax1.set_title('Расходы по категориям')
        
        # 2. Доходы vs расходы
        summary = df.groupby('type')['amount'].sum()
        income = summary.get('income', 0)
        expense = summary.get('expense', 0)
        
        if income > 0 or expense > 0:
            ax2.bar(['Доходы', 'Расходы'], [income, expense], color=['green', 'red'])
            ax2.set_title('Доходы vs Расходы')
        
        # 3. Ежедневная динамика
        df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby('date')['amount'].sum()
        ax3.plot(daily.index, daily.values, marker='o')
        ax3.set_title('Динамика по дням')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Топ категорий
        top_cats = df.groupby('category')['amount'].sum().nlargest(5)
        ax4.barh(top_cats.index, top_cats.values)
        ax4.set_title('Топ-5 категорий')
        
        plt.tight_layout()
        
        # Сохраняем график в buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        plt.close()
        
        return buffer
    
    def generate_report_text(self, df: pd.DataFrame, period_name: str) -> str:
        """Генерирует текстовую часть отчета"""
        summary = df.groupby('type')['amount'].sum()
        income = summary.get('income', 0)
        expense = summary.get('expense', 0)
        margin = income - expense
        margin_percent = (margin / income * 100) if income > 0 else 0
        
        expenses = df[df['type'] == 'expense']
        
        report_text = f"""
📊 *Отчет за {period_name}*

✅ Доходы: {income:,.0f} руб.
❌ Расходы: {expense:,.0f} руб.
💰 Маржа: {margin:,.0f} руб. ({margin_percent:.1f}%)

*Топ расходов:*
"""
        if not expenses.empty:
            for cat, amount in expenses.groupby('category')['amount'].sum().nlargest(3).items():
                report_text += f"• {cat}: {amount:,.0f} руб.\n"
        else:
            report_text += "• Нет данных о расходах\n"
        
        return report_text

# Глобальный экземпляр сервиса
report_service = ReportService()