import sqlite3


DB_NAME = "bot_database.db"
def create_table_course():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ro‘yxatdan o‘tgan foydalanuvchilar jadvali
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """
    )

    conn.commit()
    conn.close()

def add_courses(name):
    """Kursni ma'lumotlar bazasiga qo‘shish"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO courses (name)
        VALUES (?)
    """, (name,))  # 📌 Tuple bo'lishi uchun `,` qo'shildi!

    conn.commit()
    conn.close()

def update_course(course_id, new_name):
    """ Kurs nomini yangilash """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE courses
        SET name = ?
        WHERE id = ?
    """, (new_name, course_id))

    conn.commit()
    conn.close()

def delete_course(course_id):
    """ Kursni ID bo‘yicha o‘chirish """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM description WHERE course_id = ?", (course_id,))

    # Keyin kursni o‘chirish
    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()

def get_courses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id,name FROM courses")
    courses = cursor.fetchall()
    conn.close()
    return courses





