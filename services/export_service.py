# finance_bot/services/export_service.py

import os
import pandas as pd
from datetime import datetime
from services.transaction_service import transaction_service

class ExportService:
    def export_to_excel(self, user_id: int) -> str:
        """Экспортирует данные пользователя в Excel файл"""
        try:
            # Получаем транзакции пользователя
            transactions = transaction_service.get_user_transactions(user_id)
            
            if not transactions:
                return ""  # Пустая строка означает отсутствие данных
            
            # Создаем DataFrame
            data = []
            for transaction in transactions:
                data.append({
                    'date': transaction.date,
                    'type': 'Доход' if transaction.type == 'income' else 'Расход',
                    'category': transaction.category,
                    'amount': transaction.amount,
                    'description': transaction.description
                })
            
            df = pd.DataFrame(data)
            
            # Создаем имя файла
            filename = f"finance_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Сохраняем в Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Лист с транзакциями
                df.to_excel(writer, sheet_name='Транзакции', index=False)
                
                # Лист со сводкой
                summary_data = {
                    'Показатель': ['Доходы', 'Расходы', 'Баланс'],
                    'Сумма': [
                        df[df['type'] == 'Доход']['amount'].sum(),
                        df[df['type'] == 'Расход']['amount'].sum(),
                        df[df['type'] == 'Доход']['amount'].sum() - df[df['type'] == 'Расход']['amount'].sum()
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Сводка', index=False)
            
            return filename
            
        except Exception as e:
            print(f"Export error: {e}")
            return ""

    def cleanup_file(self, filename: str):
        """Удаляет временный файл после отправки"""
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"Error cleaning up file: {e}")

# Глобальный экземпляр сервиса
export_service = ExportService()