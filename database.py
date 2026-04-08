import sqlite3

def create_database():
    conn = sqlite3.connect('database/papers.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = OFF')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='subjects'")
    existing_subjects = cursor.fetchone()
    if existing_subjects and 'UNIQUE(name' in existing_subjects[0] and 'UNIQUE(name, year)' not in existing_subjects[0]:
        cursor.execute('DROP TABLE IF EXISTS subjects_new')
        cursor.execute('''
            CREATE TABLE subjects_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                year INTEGER NOT NULL,
                UNIQUE(name, year)
            )
        ''')
        cursor.execute('INSERT OR IGNORE INTO subjects_new (id, name, year) SELECT id, name, year FROM subjects')
        cursor.execute('DROP TABLE subjects')
        cursor.execute('ALTER TABLE subjects_new RENAME TO subjects')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                year INTEGER NOT NULL,
                UNIQUE(name, year)
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
        ('Mathematics', 2),
        ('Physics', 2),
        ('Data Structures with C++', 2),
        ('Advanced Networking', 2),
        ('OOP and Web Development with Java', 2),
        ('Software Engineering', 2),
        ('Advanced Database', 2),
        ('English', 2),
        ('Embedded Systems (Integrate Hardware with Software)', 2),
        ('Web 3 with Solidity', 2),
        ('3D Modelling with Blender', 2),
        ('Mathematics', 3),
        ('Physics', 3),
        ('Machine Learning with Python', 3),
        ('Cybersecurity', 3),
        ('Mobile Apps Development with React Native', 3),
        ('Information Technology with Project Management', 3),
        ('DevOps', 3),
        ('English', 3),
        ('Intelligent Robotics and Some Embedded Systems', 3),
    ])

    conn.commit()
    conn.close()
    print('RCA Year 1-3 database created successfully!')

if __name__ == '__main__':
    create_database()