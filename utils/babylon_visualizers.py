# utils/babylon_visualizers.py - ВАВИЛОНСКИЕ ВИЗУАЛИЗАЦИИ
from typing import Dict


class BabylonVisualizer:
    """
    Визуализация финансовых данных в стиле древнего Вавилона
    Пирамиды, храмы, реки - метафоры финансовой стабильности
    """
    
    @staticmethod
    def create_pyramid_chart(health_score: float, components: Dict) -> str:
        """
        Создает текстовую пирамиду финансовой стабильности
        По аналогии с вавилонскими зиккуратами
        """
        levels = {
            90: "🏛️ ВЕРШИНА: Финансовая мудрость",
            75: "🥇 УРОВЕНЬ 3: Стабильность", 
            60: "🥈 УРОВЕНЬ 2: Рост",
            40: "🥉 УРОВЕНЬ 1: Основа",
            0:  "🎯 ФУНДАМЕНТ: Начало пути"
        }
        
        # Определяем текущий уровень
        current_level = "🎯 ФУНДАМЕНТ: Начало пути"
        for threshold, level_name in sorted(levels.items(), reverse=True):
            if health_score >= threshold:
                current_level = level_name
                break
        
        pyramid = "🏔️ *ПИРАМИДА ФИНАНСОВОЙ СТАБИЛЬНОСТИ*\n\n"
        
        # Визуализация уровней пирамиды
        for threshold, level_name in sorted(levels.items(), reverse=True):
            if health_score >= threshold:
                pyramid += f"✅ {level_name}\n"
            else:
                pyramid += f"◻️ {level_name}\n"
        
        pyramid += f"\n📊 Ваш уровень: {current_level}"
        pyramid += f"\n💎 Общий счет: {health_score}/100"
        
        return pyramid
    
    @staticmethod
    def create_temple_progress(debt_progress: float, savings_ratio: float) -> str:
        """
        Визуализация прогресса в виде строительства храма
        """
        # Прогресс строительства (основа - долги, стены - накопления)
        foundation = min(100, debt_progress)  # Фундамент = прогресс по долгам
        walls = min(100, savings_ratio * 2)   # Стены = накопления
        
        temple_visual = "🏛️ *ХРАМ ВАШЕГО БОГАТСТВА*\n\n"
        
        # Визуализация храма
        if foundation >= 90 and walls >= 80:
            temple_visual += "✨ Храм завершен! Вы достигли финансовой свободы!\n"
            temple_visual += "    /¯¯¯¯¯¯¯\\\n"
            temple_visual += "   / 🏛️ 🏛️ \\\n" 
            temple_visual += "  /_________\\\n"
        elif foundation >= 50:
            temple_visual += "🏗️ Храм строится... Фундамент заложен!\n"
            temple_visual += "    /       \\\n"
            temple_visual += "   /  🧱 🧱  \\\n"
            temple_visual += "  /_________\\\n"
        else:
            temple_visual += "⛏️ Закладываем фундамент...\n"
            temple_visual += "    _________\n"
            temple_visual += "   /         \\\n"
            temple_visual += "  /___🚧___\\\n"
        
        temple_visual += f"\n📐 Фундамент (долги): {foundation}%"
        temple_visual += f"\n🧱 Стены (накопления): {walls}%"
        
        return temple_visual
    
    @staticmethod
    def create_river_flow_diagram(income: float, expenses: float, savings: float) -> str:
        """
        Диаграмма денежных потоков в виде рек Вавилона
        """
        total = income
        if total == 0:
            return "🌊 *ДЕНЕЖНЫЕ ПОТОКИ*\n\nПока нет данных о движении средств"
        
        expense_percent = (expenses / total * 100) if total > 0 else 0
        savings_percent = (savings / total * 100) if total > 0 else 0
        
        diagram = "🌊 *РЕКИ ВАВИЛОНСКИХ ФИНАНСОВ*\n\n"
        diagram += f"💧 Общий поток: {income:,.0f} руб.\n\n"
        
        # Визуализация потоков
        diagram += "📥 Входящий поток (доходы):\n"
        diagram += "▰" * 10 + " 100%\n\n"
        
        diagram += "📤 Исходящие потоки:\n"
        diagram += f"💸 Расходы: {'▰' * int(expense_percent / 10)} {expense_percent:.1f}%\n"
        diagram += f"💰 Накопления: {'▰' * int(savings_percent / 10)} {savings_percent:.1f}%\n"
        
        # Баланс
        balance_percent = 100 - expense_percent - savings_percent
        if balance_percent > 0:
            diagram += f"💼 Остаток: {'▰' * int(balance_percent / 10)} {balance_percent:.1f}%\n"
        
        return diagram
    
    @staticmethod
    def create_progress_bar(progress: float, width: int = 10) -> str:
        """Создает текстовый прогресс-бар"""
        filled = '█' * int(progress / 100 * width)
        empty = '░' * (width - int(progress / 100 * width))
        return f"{filled}{empty} {progress:.1f}%"

# Глобальный экземпляр визуализатора
babylon_visualizer = BabylonVisualizer()