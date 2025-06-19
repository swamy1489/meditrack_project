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
            return redirect('/admin_dashboard') if user[3] == 'admin' else redirect('/patient_dashboard')
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'username' not in session or session.get('role') != 'patient':
        return redirect('/login')
    return render_template('patient_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin_dashboard.html')

@app.route('/patient_appts')
def patient_appts():
    if 'username' not in session or session.get('role') != 'patient':
        return redirect('/login')
    return render_template('patient_appts.html')

@app.route('/patient_prescriptions')
def patient_prescriptions():
    if 'username' not in session or session.get('role') != 'patient':
        return redirect('/login')
    return render_template('patient_prescriptions.html')

@app.route('/patient_reports')
def patient_reports():
    if 'username' not in session or session.get('role') != 'patient':
        return redirect('/login')
    return render_template('patient_reports.html')

@app.route('/patients')
def patients():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect('/login')
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role='patient'")
    patient_list = c.fetchall()
    conn.close()
    return render_template('patients.html', patients=patient_list)

@app.route('/add_prescription', methods=['GET', 'POST'])
def add_prescription():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect('/login')
    if request.method == 'POST':
        patient = request.form['patient']
        prescription = request.form['prescription']
        conn = sqlite3.connect('meditrack.db')
        c = conn.cursor()
        c.execute("INSERT INTO prescriptions (patient, prescription) VALUES (?, ?)", (patient, prescription))
        conn.commit()
        conn.close()
        return redirect('/admin_dashboard')
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE role='patient'")
    patients = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template('add_prescription.html', patients=patients)

@app.route('/analytics')
def analytics():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect('/login')
    return render_template('analytics.html')

@app.route('/appointments')
def view_appointments():
    if 'username' not in session:
        return redirect('/login')
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute("SELECT * FROM appointments")
    appointments = c.fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments)

@app.route('/reports')
def reports():
    if 'username' not in session:
        return redirect('/login')
    return render_template('reports.html')

@app.route('/view_patients')
def view_patients():
    if 'username' not in session:
        return redirect('/login')
    patients = [
        {"id": 1, "name": "John Doe", "age": 30, "condition": "Diabetes"},
        {"id": 2, "name": "Jane Smith", "age": 45, "condition": "Hypertension"},
        {"id": 3, "name": "Ali Khan", "age": 29, "condition": "Asthma"},
    ]
    return render_template("view_patients.html", patients=patients)

@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        patient = session.get('username')
        doctor = request.form['doctor']
        date = request.form['date']
        conn = sqlite3.connect('meditrack.db')
        c = conn.cursor()
        c.execute("INSERT INTO appointments (patient, doctor, date) VALUES (?, ?, ?)", (patient, doctor, date))
        conn.commit()
        conn.close()
        return redirect('/appointments')
    return render_template('book_appointment.html')

@app.route('/upcoming-appointments')
def upcoming_appointments():
    if 'username' not in session:
        return redirect('/login')
    patient = session['username']
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute("SELECT doctor, date FROM appointments WHERE patient=?", (patient,))
    appointments = c.fetchall()
    conn.close()
    return render_template('upcoming_appointments.html', appointments=appointments)

@app.route('/admin_appointments')
def admin_appointments():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect('/login')
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute("SELECT patient, doctor, date FROM appointments")
    appointments = c.fetchall()
    conn.close()
    return render_template('admin_appts.html', appointments=appointments)

@app.route('/prescriptions')
def prescriptions():
    if 'username' not in session or session.get('role') != 'patient':
        return redirect('/login')
    patient = session['username']
    conn = sqlite3.connect('meditrack.db')
    c = conn.cursor()
    c.execute("SELECT prescription FROM prescriptions WHERE patient=?", (patient,))
    prescriptions = c.fetchall()
    conn.close()
    return render_template('prescriptions.html', prescriptions=prescriptions)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)