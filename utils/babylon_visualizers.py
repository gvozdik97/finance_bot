# utils/babylon_visualizers.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

import math
from datetime import datetime
from services.advanced_analytics import advanced_analytics
from services.wallet_service import wallet_service
from services.debt_service import debt_service

class BabylonVisualizer:
    """
    Продвинутая визуализация финансовых данных в стиле древнего Вавилона
    с исправлениями парсинга для Telegram
    """
    
    @staticmethod
    def create_financial_pyramid(user_id: int) -> str:
        """
        Создает детализированную пирамиду финансовой стабильности
        с реальными данными пользователя
        """
        try:
            health_data = advanced_analytics.calculate_financial_health_score(user_id)
            wallets = wallet_service.get_all_wallets(user_id)
            debts = debt_service.get_active_debts(user_id)
            
            pyramid = "*ПИРАМИДА ФИНАНСОВОЙ СТАБИЛЬНОСТИ ВАВИЛОНА*\n\n"
            
            # Уровни пирамиды с реальными метриками
            levels = [
                {
                    'threshold': 90,
                    'name': 'ВЕРШИНА: Финансовая мудрость',
                    'condition': health_data['total_score'] >= 90,
                    'metrics': f"Счет: {health_data['total_score']}/100"
                },
                {
                    'threshold': 75,
                    'name': 'УРОВЕНЬ 3: Стабильность и рост',
                    'condition': health_data['total_score'] >= 75,
                    'metrics': f"Золотой запас: {wallets.get('gold_reserve', 0):,.0f} руб."
                },
                {
                    'threshold': 60,
                    'name': 'УРОВЕНЬ 2: Контроль расходов',
                    'condition': health_data['total_score'] >= 60,
                    'metrics': f"Бюджет жизни: {wallets.get('living_budget', 0):,.0f} руб."
                },
                {
                    'threshold': 40,
                    'name': 'УРОВЕНЬ 1: Основа основ',
                    'condition': health_data['total_score'] >= 40,
                    'metrics': f"Долги: {sum(d.current_amount for d in debts):,.0f} руб."
                },
                {
                    'threshold': 0,
                    'name': 'ФУНДАМЕНТ: Начало пути',
                    'condition': True,
                    'metrics': "Добро пожаловать в Вавилон!"
                }
            ]
            
            for level in levels:
                status = "✅" if level['condition'] else "◻️"
                pyramid += f"{status} {level['name']}\n"
                if level['condition']:
                    pyramid += f"   {level['metrics']}\n"
            
            # Прогресс-бар текущего уровня
            current_level_progress = health_data['total_score']
            progress_bar = BabylonVisualizer.create_progress_bar(current_level_progress)
            
            pyramid += f"\nПрогресс: {progress_bar}"
            pyramid += f"\nСледующий уровень: {health_data['level']}"
            
            return pyramid
            
        except Exception as e:
            return "Пирамида финансовой стабильности\n\nДанные временно недоступны"
    
    @staticmethod
    def create_wealth_temple(user_id: int) -> str:
        """
        Создает визуализацию храма богатства с исправленным форматированием
        """
        try:
            health_data = advanced_analytics.calculate_financial_health_score(user_id)
            wallets = wallet_service.get_all_wallets(user_id)
            debts = debt_service.get_active_debts(user_id)
            
            total_wealth = sum(wallets.values())
            debt_progress = 100 - (sum(d.current_amount for d in debts) / (sum(d.initial_amount for d in debts) * 100)) if debts else 100
            savings_progress = min(100, (wallets.get('gold_reserve', 0) / max(1, total_wealth) * 200))
            
            temple = "*ХРАМ ВАШЕГО БОГАТСТВА*\n\n"
            
            # Определяем стадию строительства храма
            construction_stage = min(4, int(health_data['total_score'] / 25))
            
            stages = [
                {
                    'stage': 0,
                    'visual': "    ⛏️🔨\n   /🚧🚧🚧\\\n  /_________\\\n",
                    'description': "Закладываем фундамент..."
                },
                {
                    'stage': 1,
                    'visual': "    /¯¯¯\\\n   /🧱🧱🧱\\\n  /_________\\\n",
                    'description': "Строим стены..."
                },
                {
                    'stage': 2,
                    'visual': "    /🏛️\\\n   /🧱🧱🧱\\\n  /_________\\\n",
                    'description': "Возводим колонны..."
                },
                {
                    'stage': 3,
                    'visual': "    /🏛️🏛️\\\n   /🧱🏛️🧱\\\n  /_________\\\n",
                    'description': "Украшаем храм..."
                },
                {
                    'stage': 4,
                    'visual': "   ✨🏛️✨\n  /🏛️🏛️🏛️\\\n /_________\\\n",
                    'description': "Храм завершен!"
                }
            ]
            
            temple += stages[construction_stage]['visual']
            temple += f"\n{stages[construction_stage]['description']}\n"
            
            # Детали прогресса (без форматирования)
            temple += f"\nФундамент (свобода от долгов): {debt_progress:.1f}%"
            temple += f"\nСтены (накопления): {savings_progress:.1f}%"
            temple += f"\nКолонны (стабильность): {health_data['components'].get('income_stability', 0):.1f}%"
            temple += f"\nКрыша (финансовая мудрость): {health_data['total_score']:.1f}%"
            
            if construction_stage == 4:
                temple += "\n\nПоздравляем! Вы построили храм финансовой свободы!"
            
            return temple
            
        except Exception as e:
            return "Храм богатства\n\nИдет расчет строительных материалов..."
    
    @staticmethod
    def create_river_of_fortune(user_id: int) -> str:
        """
        Создает диаграмму денежных потоков в виде рек Месопотамии
        """
        try:
            transactions = advanced_analytics.analyze_spending_patterns(user_id)
            wallets = wallet_service.get_all_wallets(user_id)
            
            # Примерные данные
            monthly_income = 100000
            monthly_expenses = transactions.get('monthly_total', 0)
            monthly_savings = wallets.get('gold_reserve', 0) / 12
            
            diagram = "РЕКИ ФИНАНСОВОЙ УДАЧИ\n\n"
            diagram += "Древний Вавилон стоял на реках Евфрат и Тигр\n"
            diagram += "Ваши финансы текут подобно этим рекам:\n\n"
            
            # Визуализация потоков с символами
            total = max(monthly_income, monthly_expenses + monthly_savings)
            
            if total > 0:
                income_stream = "🌊" * max(1, int(monthly_income / total * 10))
                expense_stream = "💸" * max(1, int(monthly_expenses / total * 10))
                savings_stream = "💰" * max(1, int(monthly_savings / total * 10))
                
                diagram += f"Приток (доходы): {income_stream} {monthly_income:,.0f} руб.\n"
                diagram += f"Отток (расходы): {expense_stream} {monthly_expenses:,.0f} руб.\n"
                diagram += f"Накопления: {savings_stream} {monthly_savings:,.0f} руб.\n\n"
                
                # Анализ баланса
                balance = monthly_income - monthly_expenses - monthly_savings
                if balance > 0:
                    diagram += f"Положительный баланс: +{balance:,.0f} руб.\n"
                elif balance < 0:
                    diagram += f"Отрицательный баланс: {balance:,.0f} руб.\n"
                else:
                    diagram += "Сбалансированные потоки\n"
                
                # Мудрость Вавилона
                savings_ratio = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
                if savings_ratio >= 10:
                    diagram += "Мудрость: Вы соблюдаете правило 10%!"
                else:
                    diagram += "Совет: Стремитесь к 10% накоплений от доходов"
            
            return diagram
            
        except Exception as e:
            return "Реки финансовой удачи\n\nИдет измерение потоков..."
    
    @staticmethod
    def create_zodiac_financial_chart(user_id: int) -> str:
        """
        Создает финансовый гороскоп в стиле вавилонской астрологии
        """
        try:
            health_data = advanced_analytics.calculate_financial_health_score(user_id)
            wallets = wallet_service.get_all_wallets(user_id)
            
            # Вавилонские астрологические символы
            zodiac_signs = [
                "♈ Овен", "♉ Телец", "♊ Близнецы", "♋ Рак",
                "♌ Лев", "♍ Дева", "♎ Весы", "♏ Скорпион",
                "♐ Стрелец", "♑ Козерог", "♒ Водолей", "♓ Рыбы"
            ]
            
            # Определяем "финансовый знак" по балансу
            financial_balance = sum(wallets.values())
            sign_index = int(str(int(financial_balance))[-1]) % 12
            
            chart = "ФИНАНСОВЫЙ ГОРОСКОП ВАВИЛОНА\n\n"
            chart += f"Ваш финансовый знак: {zodiac_signs[sign_index]}\n\n"
            
            # Прогноз на основе данных
            if health_data['total_score'] >= 80:
                forecast = "Отличные перспективы! Звезды благоволят вашим финансам."
            elif health_data['total_score'] >= 60:
                forecast = "Хорошие возможности. Продолжайте в том же духе."
            else:
                forecast = "Время перемен. Изучите мудрость Вавилона для улучшений."
            
            chart += f"Прогноз: {forecast}\n\n"
            
            # Аспекты гороскопа
            chart += "Аспекты вашего финансового гороскопа:\n"
            
            aspects = [
                f"Золотой запас: {'Благоприятный' if wallets.get('gold_reserve', 0) > 0 else 'Требует внимания'}",
                f"Бюджет жизни: {'Сбалансированный' if wallets.get('living_budget', 0) > 0 else 'Недостаточный'}",
                f"Стабильность: {'Высокая' if health_data['components'].get('income_stability', 0) > 70 else 'Средняя'}",
                f"Дисциплина: {'Отличная' if health_data['components'].get('rule_10_percent', 0) > 80 else 'Развивающаяся'}"
            ]
            
            for aspect in aspects:
                chart += f"• {aspect}\n"
            
            chart += f"\nОбщая энергия: {health_data['total_score']}/100"
            
            return chart
            
        except Exception as e:
            return "Финансовый гороскоп\n\nЗвезды временно скрыты облаками..."
    
    @staticmethod
    def create_progress_bar(progress: float, width: int = 10) -> str:
        """Создает текстовый прогресс-бар с вавилонскими символами"""
        filled = '█' * int(progress / 100 * width)
        empty = '░' * (width - int(progress / 100 * width))
        return f"{filled}{empty} {progress:.1f}%"
    
    @staticmethod
    def create_monthly_report(user_id: int) -> str:
        """
        Создает ежемесячный отчет в стиле вавилонских летописей
        """
        try:
            health_data = advanced_analytics.calculate_financial_health_score(user_id)
            wallets = wallet_service.get_all_wallets(user_id)
            analysis = advanced_analytics.analyze_spending_patterns(user_id)
            
            current_date = datetime.now()
            month_name = current_date.strftime("%B")
            year = current_date.year
            
            report = f"ЛЕТОПИСЬ ВАВИЛОНА - {month_name.upper()} {year}\n\n"
            
            # Заголовок с уровнем
            report += f"Титул: {health_data['level']}\n"
            report += f"Финансовый счет: {health_data['total_score']}/100\n\n"
            
            # Основные метрики
            report += "ЦИФРЫ МЕСЯЦА:\n"
            report += f"• Золотой запас: {wallets.get('gold_reserve', 0):,.0f} руб.\n"
            report += f"• Бюджет жизни: {wallets.get('living_budget', 0):,.0f} руб.\n"
            report += f"• Общие расходы: {analysis.get('monthly_total', 0):,.0f} руб.\n"
            report += f"• Категорий расходов: {analysis.get('total_categories', 0)}\n\n"
            
            # Достижения месяца
            report += "ДОСТИЖЕНИЯ МЕСЯЦА:\n"
            
            achievements = []
            if health_data['total_score'] > health_data.get('previous_score', 0):
                achievements.append("Улучшение финансового здоровья")
            if wallets.get('gold_reserve', 0) > 0:
                achievements.append("Рост золотого запаса")
            if analysis.get('total_categories', 0) > 0:
                achievements.append("Активное ведение учета")
            
            if achievements:
                for achievement in achievements:
                    report += f"• ✅ {achievement}\n"
            else:
                report += "• Начните с малого - добавьте первую транзакцию\n"
            
            report += f"\nМУДРОСТЬ ВАВИЛОНА: «Летопись богатства пишется ежедневными решениями»"
            
            return report
            
        except Exception as e:
            return "Летопись Вавилона\n\nПисец временно отсутствует..."

# Глобальный экземпляр визуализатора
babylon_visualizer = BabylonVisualizer()