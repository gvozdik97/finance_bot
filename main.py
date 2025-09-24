# finance_bot/main.py

import os
from dotenv import load_dotenv
from bot.bot import run_bot

def main():
    """Основная функция запуска бота"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие токена
    if not os.getenv('BOT_TOKEN'):
        print("❌ Ошибка: BOT_TOKEN не найден в переменных окружения")
        print("Создайте файл .env и добавьте BOT_TOKEN=your_bot_token")
        return
    
    try:
        # Запускаем бота
        run_bot()
    except KeyboardInterrupt:
        print("\nБот остановлен")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()