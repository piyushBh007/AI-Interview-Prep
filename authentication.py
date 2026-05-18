import streamlit as st
from database import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already exists."
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert new user
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True, "Registration successful! Please login."
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and hash_password(password) == user['password_hash']:
            return True, user['id']
        else:
            return False, "Invalid username or password."
    except Exception as e:
        return False, f"An error occurred: {e}"
    finally:
        conn.close()

def logout_user():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
