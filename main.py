# main.py - ОБНОВЛЕННАЯ ВЕРСИЯ
import os
import time
import sqlite3
from dotenv import load_dotenv
from bot.bot import run_bot
from utils.database_recovery import recover_database

def main():
    """Основная функция запуска чистого вавилонского бота"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие токена
    if not os.getenv('BOT_TOKEN'):
        print("❌ Ошибка: BOT_TOKEN не найден в .env файле")
        print("💡 Создайте файл .env и добавьте: BOT_TOKEN=your_actual_token")
        return
    
    # Восстанавливаем базу данных при необходимости
    print("🔧 Проверка базы данных...")
    recover_database()
    
    print("🚀 Запуск Вавилонского финансового бота...")
    print("💎 Архитектура: Чистая вавилонская реализация")
    print("📊 Правила: Гибкие накопления (0-100%), бюджеты, редактирование")
    print("🎯 Цель: Финансовая мудрость по законам древнего Вавилона")
    
    try:
        run_bot()
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("🔒 База данных заблокирована. Перезапуск через 5 секунд...")
            time.sleep(5)
            recover_database()
            run_bot()
        else:
            raise e
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == '__main__':
    main()