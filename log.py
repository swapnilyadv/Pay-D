import streamlit as st
import sqlite3
from hashlib import sha256

# Initialize connection to SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT, phone TEXT, document BLOB)''')
conn.commit()

def make_hash(password):
    """Create a SHA-256 hash of the password"""
    return sha256(str.encode(password)).hexdigest()

def check_user(username, password):
    """Check if username/password combination exists in database"""
    c.execute('SELECT * FROM users WHERE username=? AND password=?',
              (username, make_hash(password)))
    return c.fetchone() is not None

def add_user(username, password, phone, document):
    """Add new user to database"""
    try:
        c.execute('INSERT INTO users VALUES (?, ?, ?, ?)', 
                 (username, make_hash(password), phone, document))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def main():
    st.title("Pay-D")
    st.title("Authentication System")
    
    menu = ["Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Login":
        st.subheader("Login Section")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        
        if st.button("Login"):
            if check_user(username, password):
                st.success(f"Logged in as {username}")
                st.balloons()
            else:
                st.error("Incorrect username or password")
                
    elif choice == "SignUp":
        st.subheader("Create New Account")
        
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')
        phone = st.text_input("Phone Number")
        document = st.file_uploader("Upload Document", type=["pdf", "docx", "jpg", "png"])
        
        if st.button("SignUp"):
            if new_password != confirm_password:
                st.error("Passwords don't match")
            elif not new_username or not new_password or not phone or not document:
                st.error("Please fill all fields and upload a document")
            else:
                document_data = document.read()
                if add_user(new_username, new_password, phone, document_data):
                    st.success("Account created successfully!")
                    st.balloons()
                else:
                    st.error("Username already exists")

if __name__ == '__main__':
    main()
