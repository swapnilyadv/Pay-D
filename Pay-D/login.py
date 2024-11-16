import streamlit as st
import sqlite3
import random
import smtplib
from hashlib import sha256
import base64

# Initialize SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, 
              email TEXT, 
              password TEXT, 
              aadharnumber INTEGER, 
              phone TEXT, 
              document BLOB)''')
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
    """Check if username/password combination exists in database"""
    hashed_password = make_hash(password)  # Hash the entered password
    c.execute('SELECT password FROM users WHERE username=?', (username,))
    record = c.fetchone()
    if record:
        stored_password = record[0]  # Retrieve the stored hash
        return stored_password == hashed_password  # Compare hashes
    return False


def add_user(username, email, password, aadhaar, otp):
    """Add user to the database"""
    try:
        hashed_password = make_hash(password)
        c.execute('INSERT INTO users (username, email, password, aadharnumber, otp) VALUES (?, ?, ?, ?, ?)', 
                  (username, email, hashed_password, aadhaar, otp))
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


# Utility function to add a logo to the homepage
# Utility function to add a logo to the homepage
def add_logo():
    """Display the Pay-D logo at the top of the page."""
    st.markdown(
        """
        <style>
            .header-logo {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: 20px;  /* Adjust margin for spacing */
                margin-bottom: 10px;  /* Adjust margin for spacing */
            }
            img {
                max-width: 100%;
                display: flex;
                justify-content: cent
                width: 150px;  /* Adjusted width for a smaller logo */
                height: auto;  /* Maintain aspect ratio */
                border-radius: 10px;  /* Optional: add rounded corners for style */
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);  /* Optional: add shadow for depth */
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Path to the logo image in the 'images' folder
    st.image("images/logo.png", use_container_width=False, width=150)  # Smaller logo centered on the page


# Function to set a background image globally
def set_background(image_file):
    """Set a background image for the Streamlit app."""
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Main Streamlit App
def main():
    # Set the background for the entire app
    set_background("images/background.jpg")  # Path to the background image in 'images' folder
    st.logo("images/logo.png", size="medium", link=None, icon_image=None)
    # st.title("Pay-D")
    
    menu = ["Home", "About Us", "GPT", "Sign In", "Sign Up"]
    
    # Only show Sign In and Sign Up if the user is not logged in
    if 'username' in st.session_state:
        menu.remove("Sign In")
        menu.remove("Sign Up")
        menu.append("Account")  # Add Account option if the user is logged in

    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Sign In":
        st.subheader("Sign In")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if check_user(username, password):
                st.session_state.username = username  # Store the username in session state
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
    
    elif choice == "Account":
        if 'username' in st.session_state:  # Check if the user is logged in
            username = st.session_state.username
            st.subheader(f"Welcome to Pay-D, {username}")
    
    elif choice == "Home":
        # Set background and logo for the Home page
        add_logo()  # Display the logo
        st.subheader("Track, Grow, Conserve – One Tree at a Time with Pay-D")
        st.write("""
        Pay-D is a tree tracking platform designed to monitor the growth and health of trees through advanced tracking technologies. Here's how it functions:
        
        **Tree Registration**: Users can register a tree by inputting its details, including species, planting location, and growth stage.
        
        **Tracking Progress**: The platform provides a dynamic map where users can track the tree's growth over time, including height, canopy spread, and overall health.
        
        **Monitoring Conditions**: Pay-D integrates environmental data to monitor factors like soil moisture, temperature, and weather patterns that affect tree growth.
        
        **Engagement & Rewards**: Users can participate in tree-related initiatives, share updates, and receive rewards or incentives for maintaining and nurturing trees.
        
        **Contribution to Conservation**: By tracking trees and promoting sustainable care, Pay-D helps contribute to environmental conservation and awareness.
        """)
    
    elif choice == "About Us":
        st.subheader("About Us")
        st.write("""
        Pay-D is a revolutionary payment platform designed to make digital transactions more secure and efficient. 
        Our goal is to provide fast, reliable, and secure payment services for everyone.
        """)
        st.write("Team Members:")
        st.write("- **Swapnil Yadav**")
        st.write("- **Raj Kiran**")
        st.write("- **Pavan J**")
        st.write("- **Hemasri Sai Lella**")
    
    elif choice == "GPT":
        st.subheader("GPT - Text and Document Processing")
        st.write("You can enter text and upload a document for processing.")
        
        # Text input for GPT
        user_input = st.text_area("Enter your text here:")
        
        # File uploader for document upload
        uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt", "docx"])
        
        if uploaded_file is not None:
            # Handle document processing (if required)
            st.write(f"File '{uploaded_file.name}' uploaded successfully.")
        
        if st.button("Submit"):
            # Handle the GPT submission logic here (e.g., call GPT model or other logic)
            st.write(f"Processing the input text: {user_input}")
            # Here you can process the input as needed.

if __name__ == '__main__':
    main()
