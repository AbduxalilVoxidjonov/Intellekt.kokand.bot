import sqlite3


DB_NAME = "bot_database.db"
def create_table_description():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS description (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
        """
    )

    conn.commit()
    conn.close()


def add_description(course_id, description):
    """ Kurs tavsifini qo‘shish yoki tekshirish """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Avval kurs uchun tavsif mavjudligini tekshiramiz
    cursor.execute("SELECT description FROM description WHERE course_id = ?", (course_id,))
    existing_description = cursor.fetchone()

    if existing_description:
        conn.close()
        return False  # Tavsif allaqachon mavjud

    # Agar mavjud bo‘lmasa, yangisini qo‘shamiz
    cursor.execute("""
        INSERT INTO description (course_id, description)
        VALUES (?, ?)
    """, (course_id, description))

    conn.commit()
    conn.close()
    return True  # Yangi tavsif qo‘shildi

def update_description(course_id, new_description):
    """ Mavjud kurs tavsifini yangilash """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE description
        SET description = ?
        WHERE course_id = ?
    """, (new_description, course_id))

    updated = cursor.rowcount > 0  # Agar hech narsa o‘zgarmasa, `False` qaytaradi

    conn.commit()
    conn.close()
    return updated

def delete_description(course_id):
    """ Kurs tavsifini o‘chirish va agar jadval bo‘sh bo‘lsa, ID ni qayta tiklash """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM description WHERE course_id = ?", (course_id,))
    conn.commit()

    # 📌 Agar jadval bo‘sh bo‘lsa, ID ni 1 dan boshlash
    cursor.execute("SELECT COUNT(*) FROM description")
    if cursor.fetchone()[0] == 0:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='description'")

    conn.commit()
    conn.close()

def get_description(course_id):
    """ Kurs ID bo‘yicha tavsifni bazadan olish """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT description
        FROM description
        WHERE course_id = ?
    """, (course_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else "❌ Bu kurs uchun tavsif mavjud emas!"