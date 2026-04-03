import sqlite3

def create_database():
    conn = sqlite3.connect('database/papers.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            year INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            paper_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            description TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')

    cursor.executemany(
        'INSERT OR IGNORE INTO subjects (name, year) VALUES (?, ?)', [
        ('Mathematics', 1),
        ('Physics', 1),
        ('Fundamentals of Programming', 1),
        ('Database', 1),
        ('English', 1),
        ('Networking', 1),
        ('PHP', 1),
        ('JavaScript', 1),
        ('Embedded Systems', 1),
        ('Web User Interface', 1),
        ('Graphical User Interface', 1),
    ])

    conn.commit()
    conn.close()
    print('RCA Year 1 database created successfully!')

if __name__ == '__main__':
    create_database()