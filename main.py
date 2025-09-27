# main.py - ЧИСТЫЙ ЗАПУСК ВАВИЛОНСКОГО БОТА

import os
from dotenv import load_dotenv
from bot.bot import run_bot

def main():
    """Основная функция запуска чистого вавилонского бота"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие токена
    if not os.getenv('BOT_TOKEN'):
        print("❌ Ошибка: BOT_TOKEN не найден в .env файле")
        print("💡 Создайте файл .env и добавьте: BOT_TOKEN=your_actual_token")
        return
    
    print("🚀 Запуск Вавилонского финансового бота...")
    print("💎 Архитектура: Чистая вавилонская реализация")
    print("📊 Правила: 10%/90%, контроль расходов, накопления")
    print("🎯 Цель: Финансовая мудрость по законам древнего Вавилона")
    
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == '__main__':
    main()