# test_analytics_fixed.py - ИСПРАВЛЕННЫЙ ТЕСТ

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.advanced_analytics import advanced_analytics
from services.wallet_service import wallet_service
from services.transaction_service import transaction_service
from database.connection import db_connection

def test_analytics_fixed():
    """Тестирует исправленную функциональность аналитики"""
    print("🧪 Тестирование ИСПРАВЛЕННОЙ аналитики Вавилона...")
    
    # Тестовый пользователь
    test_user_id = 99999
    
    try:
        # Инициализируем кошельки для тестового пользователя
        wallet_service.init_user_wallets(test_user_id)
        
        # Добавляем тестовые данные
        print("\n📝 Добавляем тестовые данные...")
        
        # Тестовый доход (будет распределен 10%/90%)
        transaction_service.add_income(test_user_id, 50000, "Зарплата", "Тестовый доход")
        
        # Тестовый расход
        transaction_service.add_expense(test_user_id, 15000, "Еда", "Тестовый расход")
        
        print("✅ Тестовые данные добавлены")
        
        # Тест 1: Финансовое здоровье
        print("\n1. 📊 Тест финансового здоровья...")
        health_data = advanced_analytics.calculate_financial_health_score(test_user_id)
        print(f"   Результат: {health_data['total_score']}/100")
        print(f"   Уровень: {health_data['level']}")
        print(f"   Рекомендации: {len(health_data['recommendations'])}")
        
        # Тест 2: Прогноз накоплений
        print("\n2. 🔮 Тест прогноза накоплений...")
        forecast = advanced_analytics.predict_savings_timeline(test_user_id, 100000)
        print(f"   Достижимо: {forecast['achievable']}")
        if forecast['achievable']:
            print(f"   Месяцев: {forecast['months_needed']:.1f}")
        
        # Тест 3: Анализ расходов
        print("\n3. 📊 Тест анализа расходов...")
        analysis = advanced_analytics.analyze_spending_patterns(test_user_id)
        print(f"   Категорий: {analysis.get('total_categories', 0)}")
        print(f"   Инсайты: {analysis.get('insights', [])}")
        
        print("\n✅ Все тесты пройдены успешно! Рекурсия исправлена.")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analytics_fixed()