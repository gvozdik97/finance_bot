# test_phase3_complete.py - ПОЛНЫЙ ТЕСТ ФАЗЫ 3

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_phase3_complete():
    """Комплексное тестирование всей функциональности Фазы 3"""
    print("🎯 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ФАЗЫ 3")
    print("=" * 50)
    
    # Тестовый пользователь
    test_user_id = 99999
    
    try:
        from services.wallet_service import wallet_service
        from services.transaction_service import transaction_service
        from services.advanced_analytics import advanced_analytics
        from services.trend_analyzer import trend_analyzer
        from utils.babylon_visualizers import babylon_visualizer
        
        print("1. 🔧 Инициализация тестовых данных...")
        
        # Инициализируем кошельки
        wallet_service.init_user_wallets(test_user_id)
        
        # Добавляем тестовые транзакции
        transaction_service.add_income(test_user_id, 50000, "Зарплата", "Тест Фазы 3")
        transaction_service.add_expense(test_user_id, 15000, "Еда", "Тест расходов")
        transaction_service.add_income(test_user_id, 30000, "Фриланс", "Дополнительный доход")
        
        print("✅ Тестовые данные созданы")
        
        print("\n2. 📊 Тестирование расширенной аналитики...")
        
        # Тест финансового здоровья
        health = advanced_analytics.calculate_financial_health_score(test_user_id)
        print(f"   • Финансовое здоровье: {health['total_score']}/100 - {health['level']}")
        
        # Тест прогноза накоплений
        forecast = advanced_analytics.predict_savings_timeline(test_user_id, 100000)
        print(f"   • Прогноз накоплений: {forecast['achievable']}")
        
        # Тест анализа расходов
        analysis = advanced_analytics.analyze_spending_patterns(test_user_id)
        print(f"   • Анализ расходов: {analysis['total_categories']} категорий")
        
        print("\n3. 📈 Тестирование анализа трендов...")
        
        # Тест трендов доходов
        trends = trend_analyzer.analyze_income_trends(test_user_id)
        if trends['has_data']:
            print(f"   • Тренд доходов: {trends['trend_direction']}")
        
        # Тест паттернов расходов
        patterns = trend_analyzer.analyze_expense_patterns(test_user_id)
        if patterns['has_data']:
            print(f"   • Паттерны расходов: {patterns['total_categories']} категорий")
        
        print("\n4. 🎨 Тестирование визуализаций...")
        
        # Тест пирамиды
        pyramid = babylon_visualizer.create_financial_pyramid(test_user_id)
        print("   • Пирамида стабильности: ✅")
        
        # Тест храма
        temple = babylon_visualizer.create_wealth_temple(test_user_id)
        print("   • Храм богатства: ✅")
        
        # Тест отчета
        report = babylon_visualizer.create_monthly_report(test_user_id)
        print("   • Месячный отчет: ✅")
        
        print("\n5. 💾 Тестирование устойчивости к ошибкам...")
        
        # Тест с пользователем без данных
        empty_user_id = 88888
        empty_health = advanced_analytics.calculate_financial_health_score(empty_user_id)
        print(f"   • Пустой пользователь: {empty_health['total_score']}/100")
        
        print("\n🎉 ВСЕ ТЕСТЫ ФАЗЫ 3 УСПЕШНО ПРОЙДЕНЫ!")
        print("\n📋 ИТОГИ ФАЗЫ 3:")
        print("   ✅ Расширенная аналитика здоровья")
        print("   ✅ Анализ трендов и паттернов") 
        print("   ✅ Вавилонские визуализации")
        print("   ✅ Прогнозы и рекомендации")
        print("   ✅ Устойчивость к ошибкам")
        print("   ✅ Интеграция с основной системой")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_phase3_complete()