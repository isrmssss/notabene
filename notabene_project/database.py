import sqlite3
import os

DB_PATH = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Чтобы возвращать данные в виде словарей
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица провайдеров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            api_key TEXT,
            base_url TEXT
        )
    ''')

    # Таблица моделей, связанных с провайдерами
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            model_code TEXT NOT NULL,
            FOREIGN KEY (provider_id) REFERENCES providers (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


# --- Функции работы с данными ---

def get_all_providers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM providers")
    providers = [dict(row) for row in cursor.fetchall()]

    # Для каждого провайдера подтягиваем его модели
    for p in providers:
        cursor.execute("SELECT * FROM models WHERE provider_id = ?", (p['id'],))
        p['models'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return providers


def save_provider_with_models(provider_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Добавляем или обновляем провайдера
        cursor.execute('''
            INSERT INTO providers (name, api_key, base_url)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                api_key=excluded.api_key,
                base_url=excluded.base_url
        ''', (provider_data['name'], provider_data.get('api_key'), provider_data.get('base_url')))

        # Получаем id провайдера
        cursor.execute("SELECT id FROM providers WHERE name = ?", (provider_data['name'],))
        provider_id = cursor.fetchone()['id']

        # Удаляем старые модели провайдера, чтобы перезаписать их новыми
        cursor.execute("DELETE FROM models WHERE provider_id = ?", (provider_id,))

        # Записываем новые модели
        for model in provider_data.get('models', []):
            cursor.execute('''
                INSERT INTO models (provider_id, name, model_code)
                VALUES (?, ?, ?)
            ''', (provider_id, model['name'], model['model_code']))

        conn.commit()
        return {"status": "success", "provider_id": provider_id}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


# Инициализируем БД при импорте модуля
if not os.path.exists(DB_PATH):
    init_db()