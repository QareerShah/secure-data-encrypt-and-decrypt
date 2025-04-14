import streamlit as st
import hashlib
import re
from cryptography.fernet import Fernet

# Heading for the application
st.title("🔐 Secure Data Encryption App")
st.subheader("Encrypt and store your sensitive data securely")


# Key for Fernet encryption
if "cipher" not in st.session_state:
    st.session_state.KEY = Fernet.generate_key()
    st.session_state.cipher = Fernet(st.session_state.KEY)

# In-memory databases
if "users" not in st.session_state:
    st.session_state.users = {}  # {"username": "hashed_password"}

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "data_store" not in st.session_state:
    st.session_state.data_store = {}  # {"username": {"encrypted": "...", "passkey": "..."}}

if "show_login" not in st.session_state:
    st.session_state.show_login = False

# Utils
def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def password_strength(password):
    strength = 0
    if len(password) >= 8: strength += 1
    if re.search(r"[A-Z]", password): strength += 1
    if re.search(r"[0-9]", password): strength += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): strength += 1
    return strength

def show_password_strength_meter(pwd):
    strength = password_strength(pwd)
    st.progress(strength / 4)
    if strength == 0:
        st.info("Very Weak 🔴")
    elif strength == 1:
        st.warning("Weak 🟠")
    elif strength == 2:
        st.info("Moderate 🟡")
    elif strength == 3:
        st.success("Strong 🟢")
    elif strength == 4:
        st.success("Very Strong 🟢🟢")

# Auth Flow
def signup():
    st.title("📝 Signup")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")

    if password:
        show_password_strength_meter(password)

    if st.button("Signup"):
        if username and password:
            if username in st.session_state.users:
                st.error("User already exists. Try logging in.")
            else:
                st.session_state.users[username] = hash_text(password)
                st.success("Signup successful! Please login now.")
                st.session_state.show_login = True  
                st.rerun() 
        else:
            st.error("All fields are required.")

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == hash_text(password):
            st.session_state.is_authenticated = True
            st.session_state.current_user = username
            st.success("Login successful!")
            st.rerun()  
        else:
            st.error("Invalid credentials!")


# Main secure pages
def encrypt_store():
    st.subheader("🔒 Encrypt & Store Data")
    text = st.text_area("Enter text to encrypt")
    passkey = st.text_input("Set passkey for encryption", type="password")

    if st.button("Encrypt & Save"):
        if text and passkey:
            hashed_pass = hash_text(passkey)
            encrypted = st.session_state.cipher.encrypt(text.encode()).decode()
            st.session_state.data_store[st.session_state.current_user] = {
                "encrypted": encrypted,
                "passkey": hashed_pass
            }
            st.success("Data encrypted and stored successfully.")
        else:
            st.error("Please enter all fields.")

def retrieve_decrypt():
    st.subheader("🔓 Retrieve & Decrypt Data")
    user_data = st.session_state.data_store.get(st.session_state.current_user)

    if user_data:
        st.write("🔐 Encrypted Text:")
        st.code(user_data["encrypted"])
        passkey = st.text_input("Enter Passkey to Decrypt", type="password")

        if st.button("Decrypt"):
            if hash_text(passkey) == user_data["passkey"]:
                decrypted = st.session_state.cipher.decrypt(user_data["encrypted"].encode()).decode()
                st.success("Decrypted Data:")
                st.write(decrypted)
            else:
                st.error("Incorrect passkey!")
    else:
        st.info("No data stored yet.")

def logout():
    st.session_state.is_authenticated = False
    st.session_state.current_user = None
    st.session_state.show_login = True
    st.success("Logged out successfully!")

# Main App Logic
if not st.session_state.is_authenticated:
    if st.session_state.show_login:
        login()
    else:
        signup()
else:
    # Sidebar Navigation
    st.sidebar.title("🔐 Navigation")
    selection = st.sidebar.radio("Go to", ["Encrypt & Store", "Retrieve & Decrypt", "Logout"])

    st.sidebar.markdown("---")
    st.sidebar.info(f"👤 Logged in as: `{st.session_state.current_user}`")

    if selection == "Encrypt & Store":
        encrypt_store()
    elif selection == "Retrieve & Decrypt":
        retrieve_decrypt()
    elif selection == "Logout":
        logout()
    else:
        st.error("Invalid selection!")
        logout()