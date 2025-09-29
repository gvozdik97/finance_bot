# utils/database_recovery.py
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

def recover_database(db_path='finance.db'):
    """Восстанавливает базу данных при блокировках"""
    try:
        # Пытаемся закрыть все соединения
        if os.path.exists(db_path):
            # Удаляем временные файлы SQLite
            temp_files = [
                db_path + '-wal',
                db_path + '-shm',
                db_path + '-journal'
            ]
            
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"🗑️ Удален временный файл: {temp_file}")
            
            # Проверяем целостность базы
            conn = sqlite3.connect(db_path, timeout=30.0)
            cursor = conn.cursor()
            
            # Проверяем целостность
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            if integrity == 'ok':
                print("✅ База данных цела")
            else:
                print(f"⚠️ Проблемы с базой: {integrity}")
            
            # Включаем WAL mode
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            
            conn.close()
            print("✅ База данных восстановлена")
            
        else:
            print("📁 База данных не существует, будет создана при запуске")
            
    except Exception as e:
        print(f"❌ Ошибка восстановления: {e}")

if __name__ == "__main__":
    recover_database()