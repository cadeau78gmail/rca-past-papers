from flask import Flask, render_template, request, redirect, session, send_file
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'rca_secret_key_2024'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def get_db():
    conn = sqlite3.connect('database/papers.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect('/home')

@app.route('/home')
def index():
    conn = get_db()
    subjects = conn.execute('''
        SELECT subjects.*,
        COUNT(papers.id) as paper_count
        FROM subjects
        LEFT JOIN papers ON subjects.id = papers.subject_id
        GROUP BY subjects.id
    ''').fetchall()
    total_papers = conn.execute(
        'SELECT COUNT(*) FROM papers').fetchone()[0]
    total_subjects = conn.execute(
        'SELECT COUNT(*) FROM subjects').fetchone()[0]
    recent_papers = conn.execute('''
        SELECT papers.*, subjects.name as subject_name
        FROM papers JOIN subjects
        ON papers.subject_id = subjects.id
        ORDER BY papers.uploaded_at DESC LIMIT 5
    ''').fetchall()
    conn.close()
    return render_template('index.html',
        subjects=subjects,
        total_papers=total_papers,
        total_subjects=total_subjects,
        recent_papers=recent_papers,
        current_year=datetime.now().year)

@app.route('/browse')
def browse():
    conn = get_db()
    subjects = conn.execute(
        'SELECT * FROM subjects').fetchall()
    years = list(range(datetime.now().year, 2019, -1))

    search = request.args.get('search', '')
    selected_subject = request.args.get('subject', '')
    selected_year = request.args.get('year', '')
    selected_type = request.args.get('paper_type', '')

    query = '''SELECT papers.*, subjects.name as subject_name
               FROM papers JOIN subjects
               ON papers.subject_id = subjects.id
               WHERE 1=1'''
    params = []

    if search:
        query += ' AND papers.title LIKE ?'
        params.append('%' + search + '%')
    if selected_subject:
        query += ' AND papers.subject_id = ?'
        params.append(selected_subject)
    if selected_year:
        query += ' AND papers.year = ?'
        params.append(selected_year)
    if selected_type:
        query += ' AND papers.paper_type = ?'
        params.append(selected_type)

    query += ' ORDER BY papers.uploaded_at DESC'
    all_papers = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('browse.html',
        papers=all_papers,
        subjects=subjects,
        years=years,
        search=search,
        selected_subject=selected_subject,
        selected_year=selected_year,
        selected_type=selected_type)

@app.route('/view/<int:paper_id>')
def view_paper(paper_id):
    conn = get_db()
    paper = conn.execute(
        'SELECT * FROM papers WHERE id = ?', (paper_id,)
    ).fetchone()
    conn.close()
    if paper and os.path.exists(paper['file_path']):
        return send_file(paper['file_path'])
    return 'File not found', 404

@app.route('/student-download/<int:paper_id>')
def student_download(paper_id):
    conn = get_db()
    paper = conn.execute(
        'SELECT * FROM papers WHERE id = ?', (paper_id,)
    ).fetchone()
    conn.close()
    if paper and os.path.exists(paper['file_path']):
        return send_file(
            paper['file_path'],
            as_attachment=True,
            download_name=paper['title'] + '.' + paper['file_type']
        )
    return 'File not found', 404

@app.route('/admin/login')
def admin_login():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            return render_template('login.html',
                error='Wrong username or password!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    total_papers = conn.execute(
        'SELECT COUNT(*) FROM papers').fetchone()[0]
    total_subjects = conn.execute(
        'SELECT COUNT(*) FROM subjects').fetchone()[0]
    conn.close()
    return render_template('dashboard.html',
        username=session['username'],
        total_papers=total_papers,
        total_subjects=total_subjects)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    subjects = conn.execute('SELECT * FROM subjects').fetchall()
    current_year = datetime.now().year
    years = list(range(current_year, 2019, -1))

    if request.method == 'POST':
        title = request.form['title']
        subject_id = request.form['subject_id']
        year = request.form['year']
        paper_type = request.form['paper_type']
        description = request.form['description']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            file_type = filename.rsplit('.', 1)[1].lower()

            conn.execute('''
                INSERT INTO papers
                (title, subject_id, year, paper_type,
                file_path, file_type, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, subject_id, year, paper_type,
                  file_path, file_type, description))
            conn.commit()
            conn.close()
            return render_template('upload.html',
                subjects=subjects,
                years=years,
                current_year=current_year,
                success='File uploaded successfully!')
        else:
            conn.close()
            return render_template('upload.html',
                subjects=subjects,
                years=years,
                current_year=current_year,
                error='Invalid file type!')

    conn.close()
    return render_template('upload.html',
        subjects=subjects,
        years=years,
        current_year=current_year)

@app.route('/papers')
def papers():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    subjects = conn.execute('SELECT * FROM subjects').fetchall()
    selected_subject = request.args.get('subject', '')
    selected_type = request.args.get('paper_type', '')

    query = '''SELECT papers.*, subjects.name as subject_name
               FROM papers JOIN subjects
               ON papers.subject_id = subjects.id
               WHERE 1=1'''
    params = []

    if selected_subject:
        query += ' AND papers.subject_id = ?'
        params.append(selected_subject)
    if selected_type:
        query += ' AND papers.paper_type = ?'
        params.append(selected_type)

    query += ' ORDER BY papers.uploaded_at DESC'
    all_papers = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('papers.html',
        papers=all_papers,
        subjects=subjects,
        selected_subject=selected_subject,
        selected_type=selected_type)

@app.route('/download/<int:paper_id>')
def download(paper_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    paper = conn.execute(
        'SELECT * FROM papers WHERE id = ?', (paper_id,)
    ).fetchone()
    conn.close()
    if paper and os.path.exists(paper['file_path']):
        return send_file(
            paper['file_path'],
            as_attachment=True,
            download_name=paper['title'] + '.' + paper['file_type']
        )
    return 'File not found', 404

@app.route('/delete/<int:paper_id>')
def delete(paper_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    paper = conn.execute(
        'SELECT * FROM papers WHERE id = ?', (paper_id,)
    ).fetchone()
    if paper:
        if os.path.exists(paper['file_path']):
            os.remove(paper['file_path'])
        conn.execute(
            'DELETE FROM papers WHERE id = ?', (paper_id,))
        conn.commit()
    conn.close()
    return redirect('/papers')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/home')

if __name__ == '__main__':
    app.run(debug=True)