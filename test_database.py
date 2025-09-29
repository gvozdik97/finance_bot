# test_database.py
import sqlite3
import threading
import time

def test_database_locking():
    """Тестирует работу с базой данных из нескольких потоков"""
    print("🧪 Тестирование работы с базой данных...")
    
    def worker(thread_id):
        """Рабочая функция для тестирования"""
        try:
            conn = sqlite3.connect('finance.db', timeout=30.0)
            cursor = conn.cursor()
            
            # Тестируем разные операции
            cursor.execute("SELECT COUNT(*) FROM sqlite_master")
            count = cursor.fetchone()[0]
            
            cursor.execute("INSERT OR IGNORE INTO user_settings (user_id, savings_rate) VALUES (?, ?)", 
                         (thread_id, 10.0))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Поток {thread_id} завершил работу")
            
        except Exception as e:
            print(f"❌ Поток {thread_id} ошибка: {e}")
    
    # Запускаем несколько потоков
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Ждем завершения всех потоков
    for t in threads:
        t.join()
    
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_database_locking()