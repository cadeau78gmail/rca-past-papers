import sqlite3
from werkzeug.security import generate_password_hash

def create_admin():
    conn = sqlite3.connect('database/papers.db')
    cursor = conn.cursor()

    username = 'admin'
    password = generate_password_hash('rca2024')

    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
        (username, password, 'admin')
    )

    conn.commit()
    conn.close()
    print('Admin account created!')
    print('Username: admin')
    print('Password: rca2024')

if __name__ == '__main__':
    create_admin()