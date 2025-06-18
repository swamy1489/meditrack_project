from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database
def init_db():
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient TEXT,
                    doctor TEXT,
                    date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient TEXT,
                    prescription TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient TEXT,
                    report TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('meditrack.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['role'] = user[3]
            if user[3] == 'admin':
                return redirect('/admin_dashboard')
            else:
                return redirect('/patient_dashboard')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        conn = sqlite3.connect('meditrack.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
        except sqlite3.IntegrityError:
            return 'Username already exists'
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/patient_dashboard')
def patient_dashboard():
    return render_template('patient_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/patient_appts')
def patient_appts():
    return render_template('patient_appts.html')

@app.route('/patient_prescriptions')
def patient_prescriptions():
    return render_template('patient_prescriptions.html')

@app.route('/patient_reports')
def patient_reports():
    return render_template('patient_reports.html')

@app.route('/patients')
def patients():
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role='patient'")
    patient_list = c.fetchall()
    conn.close()
    return render_template('patients.html', patients=patient_list)

@app.route('/add_prescription', methods=['GET', 'POST'])
def add_prescription():
    if request.method == 'POST':
        patient = request.form['patient']
        prescription = request.form['prescription']
        conn = sqlite3.connect('meditrack.db')
        c = conn.cursor()
        c.execute("INSERT INTO prescriptions (patient, prescription) VALUES (?, ?)", (patient, prescription))
        conn.commit()
        conn.close()
        return redirect('/admin_dashboard')
    return render_template('add_prescription.html')

@app.route('/admin_appts')
def admin_appts():
    return render_template('admin_appts.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/appointments')
def view_appointments():
    return render_template('appointments.html')

@app.route('/prescriptions')
def prescriptions():
    return render_template('prescriptions.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/view_patients')
def view_patients():
    patients = [
        {"id": 1, "name": "John Doe", "age": 30, "condition": "Diabetes"},
        {"id": 2, "name": "Jane Smith", "age": 45, "condition": "Hypertension"},
        {"id": 3, "name": "Ali Khan", "age": 29, "condition": "Asthma"},
    ]
    return render_template("view_patients.html", patients=patients)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)