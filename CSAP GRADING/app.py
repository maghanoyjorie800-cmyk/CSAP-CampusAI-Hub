from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from predictive_model import predict_student
from generative_ai import generate_answer, generate_study_plan

app = Flask(__name__)
app.secret_key = os.environ.get("CAMPUSAI_SECRET_KEY", "campusai-demo-secret-change-before-deployment")
DB_PATH = os.path.join(os.path.dirname(__file__), "campusai_accounts.db")

STUDENTS = [
{"id":1,"name":"Alex Santos","course":"BS Information Technology","year":"2nd Year","attendance":94,"study":9,"assignments":91,"quiz":88,"previous":90},
{"id":2,"name":"Maria Reyes","course":"BS Computer Science","year":"1st Year","attendance":86,"study":6,"assignments":82,"quiz":79,"previous":84},
{"id":3,"name":"Joshua Cruz","course":"BS Information Systems","year":"3rd Year","attendance":91,"study":8,"assignments":87,"quiz":85,"previous":88},
{"id":4,"name":"Sofia Garcia","course":"BS Information Technology","year":"2nd Year","attendance":78,"study":4,"assignments":73,"quiz":70,"previous":76}]

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student', status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        # Preserve the original demo logins.
        for name, email, username, password, role in [
            ('Teacher Admin','teacher@campusai.local','teacher','teacher123','teacher'),
            ('Alex Santos','student@campusai.local','student','student123','student')]:
            found = con.execute('SELECT id FROM accounts WHERE username=?', (username,)).fetchone()
            if not found:
                con.execute('INSERT INTO accounts(name,email,username,password_hash,role,status) VALUES(?,?,?,?,?,?)',
                    (name,email,username,generate_password_hash(password),role,'approved'))
init_db()

@app.route('/')
def index():
    return redirect(url_for('dashboard') if session.get('user') else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','').strip().lower()
        p = request.form.get('password','')
        with db() as con:
            account = con.execute('SELECT * FROM accounts WHERE lower(username)=?', (u,)).fetchone()
        if account and check_password_hash(account['password_hash'], p):
            if account['status'] != 'approved':
                msg = 'Your account is awaiting teacher admin approval.' if account['status']=='pending' else 'This account was not approved. Please contact the teacher admin.'
                return render_template('login.html', error=msg)
            session['user'] = {'id': account['id'], 'name': account['name'], 'role': account['role'], 'username': account['username']}
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        username = request.form.get('username','').strip().lower()
        password = request.form.get('password','')
        confirm = request.form.get('confirm_password','')
        if not all([name,email,username,password,confirm]):
            return render_template('register.html', error='Please complete every field.')
        if len(username) < 3 or any(ch.isspace() for ch in username):
            return render_template('register.html', error='Username must be at least 3 characters and contain no spaces.')
        if len(password) < 8:
            return render_template('register.html', error='Password must be at least 8 characters long.')
        if password != confirm:
            return render_template('register.html', error='Passwords do not match.')
        try:
            with db() as con:
                con.execute('INSERT INTO accounts(name,email,username,password_hash,role,status) VALUES(?,?,?,?,?,?)',
                    (name,email,username,generate_password_hash(password),'student','pending'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='That username is already taken. Please choose another.')
        return render_template('register.html', success='Account request submitted! You can sign in after the teacher admin approves it.')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('user'): return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/api/accounts')
def accounts():
    if session.get('user',{}).get('role') != 'teacher': return jsonify({'error':'Teacher access required'}),403
    with db() as con:
        rows = con.execute('SELECT id,name,email,username,role,status,created_at FROM accounts ORDER BY CASE status WHEN "pending" THEN 0 WHEN "approved" THEN 1 ELSE 2 END, id DESC').fetchall()
    return jsonify([dict(row) for row in rows])

@app.route('/api/accounts/<int:account_id>/<action>', methods=['POST'])
def account_action(account_id, action):
    if session.get('user',{}).get('role') != 'teacher': return jsonify({'error':'Teacher access required'}),403
    if action not in ('approve','reject'): return jsonify({'error':'Invalid action'}),400
    with db() as con:
        account = con.execute('SELECT id,username,role,status FROM accounts WHERE id=?', (account_id,)).fetchone()
        if not account: return jsonify({'error':'Account not found'}),404
        if account['role'] == 'teacher': return jsonify({'error':'Teacher admin accounts cannot be changed here.'}),400
        new_status = 'approved' if action == 'approve' else 'rejected'
        con.execute('UPDATE accounts SET status=? WHERE id=?', (new_status,account_id))
    return jsonify({'success':True,'status':new_status})

@app.route('/api/students')
def students(): return jsonify(STUDENTS)

@app.route('/api/predict',methods=['POST'])
def predict(): return jsonify(predict_student(request.get_json(force=True)))

@app.route('/api/chat',methods=['POST'])
def chat(): return jsonify({'answer':generate_answer(request.get_json(force=True).get('message',''))})

@app.route('/api/study-plan',methods=['POST'])
def plan():
    d=request.get_json(force=True); return jsonify({'plan':generate_study_plan(d.get('topic',''),d.get('hours',6))})

@app.route('/api/record',methods=['POST'])
def record():
    if session.get('user',{}).get('role')!='teacher': return jsonify({'error':'Teacher access required'}),403
    d=request.get_json(force=True); s=next((x for x in STUDENTS if x['id']==int(d['id'])),None)
    if not s:return jsonify({'error':'Student not found'}),404
    for k in ['attendance','study','assignments','quiz','previous']:
        if k in d:s[k]=float(d[k])
    return jsonify({'success':True,'student':s})

if __name__=='__main__': app.run(debug=True)
