import sqlite3

DB_NAME = "bot_database.db"


# Ma’lumotlar bazasini yaratish va ulash
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ro‘yxatdan o‘tgan foydalanuvchilar jadvali
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            address TEXT NOT NULL,
            phone_number TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


# Yangi foydalanuvchini qo‘shish
def add_user(user_id, full_name, age, address, phone_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Foydalanuvchini qo‘shish
    cursor.execute("""
            INSERT INTO users (id, full_name, age, address, phone_number)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, full_name, age, address, phone_number))

    conn.commit()
    conn.close()

def update_user(user_id, full_name, age, address, phone_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET full_name = ?, age = ?, address = ?, phone_number = ? WHERE id = ?",
        (full_name, age, address, phone_number, user_id)
    )
    conn.commit()
    conn.close()


# Foydalanuvchi ma’lumotlarini olish
def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user  # (id, full_name, age, address, phone_number) tuzilishda qaytaradi

def chech_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # agar foydalanuvchi bazada mavjud bo'lsa True qaytaradi
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return True if user else False
def get_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id,full_name, phone_number FROM users")
    users = cursor.fetchall()

    conn.close()
    return users  # (id, full_name, phone_number) tuzilishda qaytaradi

def get_user_shartnoma(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT full_name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user if user else None  # (id, full_name, age, address, phone_number) tuzilishda qaytaradi

