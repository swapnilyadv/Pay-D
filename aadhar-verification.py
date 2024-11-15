import streamlit as st
import sqlite3
import random
import smtplib
from hashlib import sha256

# Initialize SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Ensure the table has the correct schema
c.execute('DROP TABLE IF EXISTS users')  # Optional: Drop if you want to reset
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT,
    aadhaar TEXT UNIQUE,
    otp TEXT
)
''')
conn.commit()


# Utility Functions
def make_hash(password):
    """Create a SHA-256 hash of the password"""
    return sha256(password.encode()).hexdigest()

def send_otp(email, otp):
    """Send OTP to the user's email"""
    sender_email = "swapnilyadav1229@gmail.com"
    sender_password = "rmvd ifod peod xefy"  # Use the generated App Password
    receiver_email = email
    subject = "Pay-D OTP Verification"
    message = f"Subject:{subject}\n\nYour OTP for Pay-D verification is: {otp}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)
        return True
    except Exception as e:
        st.error(f"Failed to send OTP: {e}")
        return False


def check_user(username, password):
    """Check if user credentials are valid"""
    c.execute('SELECT * FROM users WHERE username=? AND password=?', 
              (username, make_hash(password)))
    return c.fetchone() is not None

def add_user(username, email, password, aadhaar, otp):
    """Add user to the database"""
    try:
        c.execute('INSERT INTO users (username, email, password, aadhaar, otp) VALUES (?, ?, ?, ?, ?)', 
                  (username, email, make_hash(password), aadhaar, otp))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_otp(username, entered_otp):
    """Verify the OTP for the user"""
    c.execute('SELECT otp FROM users WHERE username=?', (username,))
    record = c.fetchone()
    if record and record[0] == entered_otp:
        c.execute('UPDATE users SET otp=NULL WHERE username=?', (username,))
        conn.commit()
        return True
    return False

# Main Streamlit App
def main():
    st.title("Pay-D Authentication System")
    
    menu = ["Sign In", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Sign In":
        st.subheader("Sign In")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if check_user(username, password):
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password.")
    
    elif choice == "Sign Up":
        st.subheader("Sign Up")
        
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        aadhaar = st.text_input("Aadhaar Number (12 digits)", max_chars=12)
        otp = random.randint(100000, 999999)
        
        if st.button("Generate OTP"):
            if len(aadhaar) == 12 and aadhaar.isdigit():
                if send_otp(email, otp):
                    st.success("OTP has been sent to your email.")
                    st.session_state['otp'] = otp
                else:
                    st.error("Failed to send OTP. Please check your email.")
            else:
                st.error("Invalid Aadhaar number.")
        
        entered_otp = st.text_input("Enter OTP", max_chars=6)
        
        if st.button("Sign Up"):
            if 'otp' in st.session_state and int(entered_otp) == st.session_state['otp']:
                if add_user(username, email, password, aadhaar, str(otp)):
                    st.success("Account created successfully! Please log in.")
                else:
                    st.error("Username or Aadhaar already exists.")
            else:
                st.error("Invalid OTP or OTP expired.")

if __name__ == '__main__':
    main()
