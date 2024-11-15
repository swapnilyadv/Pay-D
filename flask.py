from flask import Flask, request, jsonify, render_template
import sqlite3
import random
import smtplib

app = Flask(__name__)

# Database setup
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT,
    aadhaar TEXT,
    otp TEXT
)
''')
conn.commit()

# Utility functions
def send_otp(email, otp):
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    receiver_email = email
    message = f"Your OTP for Pay-D is: {otp}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    username = data['username']
    email = data['email']
    password = data['password']
    aadhaar = data['aadhaar']
    otp = str(random.randint(100000, 999999))
    
    # Send OTP to email
    send_otp(email, otp)
    
    # Store user data
    try:
        cursor.execute('INSERT INTO users (username, email, password, aadhaar, otp) VALUES (?, ?, ?, ?, ?)',
                       (username, email, password, aadhaar, otp))
        conn.commit()
        return jsonify({"message": "User registered. Verify OTP sent to your email."})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists."})

@app.route('/signin', methods=['POST'])
def signin():
    data = request.form
    username = data['username']
    password = data['password']
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    if user:
        return jsonify({"message": f"Welcome back, {username}!"})
    return jsonify({"error": "Invalid username or password."})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.form
    username = data['username']
    otp = data['otp']
    cursor.execute('SELECT otp FROM users WHERE username=?', (username,))
    stored_otp = cursor.fetchone()
    if stored_otp and stored_otp[0] == otp:
        return jsonify({"message": "OTP Verified. Sign-Up successful!"})
    return jsonify({"error": "Invalid OTP."})

if __name__ == "__main__":
    app.run(debug=True)
