import streamlit as st
import hashlib
import re
from cryptography.fernet import Fernet

# ------------------------ Initialization ------------------------
st.set_page_config(page_title="Secure Encryption App", page_icon="🔐")

# Header
st.title("🔐 Secure Data Encryption App")
st.subheader("Encrypt and store your sensitive data securely")

# Session state initialization
if "KEY" not in st.session_state:
    st.session_state.KEY = Fernet.generate_key()
    st.session_state.cipher = Fernet(st.session_state.KEY)

st.session_state.setdefault("users", {})  # {"username": "hashed_password"}
st.session_state.setdefault("is_authenticated", False)
st.session_state.setdefault("current_user", None)
st.session_state.setdefault("data_store", {})  # {"username": {"encrypted": "...", "passkey": "..."}}
st.session_state.setdefault("show_login", False)

# ------------------------ Utility Functions ------------------------

def hash_text(text: str):
    return hashlib.sha256(text.encode()).hexdigest()

def password_strength(password):
    strength = sum([
        len(password) >= 8,
        bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"[0-9]", password)),
        bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
    ])
    return strength

def show_password_strength_meter(password):
    strength = password_strength(password)
    st.progress(strength / 4)
    levels = [
        "Very Weak 🔴", "Weak 🟠", "Moderate 🟡", "Strong 🟢", "Very Strong 🟢🟢"
    ]
    st.info(levels[strength])

# ------------------------ Auth Functions ------------------------

def signup():
    st.title("📝 Signup")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")

    if password:
        show_password_strength_meter(password)

    if st.button("Signup"):
        if not username or not password:
            st.error("All fields are required.")
            return

        if username in st.session_state.users:
            st.error("User already exists. Try logging in.")
        else:
            st.session_state.users[username] = hash_text(password)
            st.success("Signup successful! Please login.")
            st.session_state.show_login = True

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.error("All fields are required.")
            return

        if username in st.session_state.users and st.session_state.users[username] == hash_text(password):
            st.session_state.is_authenticated = True
            st.session_state.current_user = username
            st.success("Login successful!")
        else:
            st.error("Invalid credentials.")

def logout():
    st.session_state.is_authenticated = False
    st.session_state.current_user = None
    st.session_state.show_login = True
    st.success("Logged out successfully.")

# ------------------------ Secure Features ------------------------

def encrypt_store():
    st.subheader("🔒 Encrypt & Store Data")
    text = st.text_area("Enter text to encrypt")
    passkey = st.text_input("Set passkey for encryption", type="password")

    if st.button("Encrypt & Save"):
        if not text or not passkey:
            st.error("Please enter all fields.")
            return

        hashed_pass = hash_text(passkey)
        encrypted = st.session_state.cipher.encrypt(text.encode()).decode()
        st.session_state.data_store[st.session_state.current_user] = {
            "encrypted": encrypted,
            "passkey": hashed_pass
        }
        st.success("Data encrypted and stored successfully.")

def retrieve_decrypt():
    st.subheader("🔓 Retrieve & Decrypt Data")
    user_data = st.session_state.data_store.get(st.session_state.current_user)

    if not user_data:
        st.info("No data stored yet.")
        return

    st.code(user_data["encrypted"], language="text")
    passkey = st.text_input("Enter Passkey to Decrypt", type="password")

    if st.button("Decrypt"):
        if hash_text(passkey) == user_data["passkey"]:
            decrypted = st.session_state.cipher.decrypt(user_data["encrypted"].encode()).decode()
            st.success("Decrypted Data:")
            st.write(decrypted)
        else:
            st.error("Incorrect passkey.")

# ------------------------ Main Logic ------------------------

if not st.session_state.is_authenticated:
    if st.session_state.show_login:
        login()
    else:
        signup()
else:
    st.sidebar.title("🔐 Navigation")
    choice = st.sidebar.radio("Choose Action", ["Encrypt & Store", "Retrieve & Decrypt", "Logout"])

    st.sidebar.markdown("---")
    st.sidebar.info(f"👤 Logged in as: `{st.session_state.current_user}`")

    if choice == "Encrypt & Store":
        encrypt_store()
    elif choice == "Retrieve & Decrypt":
        retrieve_decrypt()
    elif choice == "Logout":
        logout()
