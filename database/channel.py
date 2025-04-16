import  sqlite3

DB_NAME = "bot_database.db"

def create_channel_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """
    )

    conn.commit()
    conn.close()

def add_channel(name):
    """Yangi kanalni bazaga qo‘shish"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO channels (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Kanal nomi allaqachon mavjud bo‘lsa
    finally:
        conn.close()


def get_channels():
    """Bazadan barcha kanallarni olish (faqat nomlarini)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM channels")
    channels = cursor.fetchall()

    conn.close()
    return [channel[0] for channel in channels]  # [(name1,), (name2,)] → [name1, name2]

def update_channel(old_channel, new_channel):
    """ Kanal nomini yangilash """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE channels
        SET name = ?
        WHERE id = ?
    """, (new_channel, old_channel))

    conn.commit()
    conn.close()

def delete_channel(channel_name):
    """ Kanalni ID bo‘yicha o‘chirish """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM channels WHERE name = ?", (channel_name,))
    conn.commit()
    conn.close()