from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DB Setup
def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.close()

init_db()

# Email validation
def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Signup
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        if not valid_email(user):
            flash("Invalid Email ❌")
            return redirect('/signup')

        if len(pwd) < 6:
            flash("Password too short ❌")
            return redirect('/signup')

        hashed_pwd = generate_password_hash(pwd)

        try:
            conn = sqlite3.connect("users.db")
            conn.execute("INSERT INTO users (username,password) VALUES (?,?)",(user,hashed_pwd))
            conn.commit()
            conn.close()
            flash("Signup Success ✅")
            return redirect('/login')
        except:
            flash("User already exists ❌")
            return redirect('/signup')

    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (user,))
        data = cur.fetchone()
        conn.close()

        if data and check_password_hash(data[2], pwd):
            session['user'] = user
            flash("Login Success ✅")
            return redirect('/dashboard')
        else:
            flash("Invalid Credentials ❌")
            return redirect('/login')

    return render_template('login.html')

# Dashboard (Protected)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect('/login')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out ✅")
    return redirect('/login')

@app.route('/')
def home():
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)