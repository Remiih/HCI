import sqlite3
import pandas as pd
from contextlib import contextmanager

DB_NAME = "inventory_system.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

import auth # Need to hash password

# ... (imports)

def init_db():
    """Initialize the database tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # ... (Create tables logic existing) ...
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                totp_secret TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        # Migration: Check if role column exists for existing DBs
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'role' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        
        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0.0,
                description TEXT
            )
        ''')

        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    # --- Default Admin Creation ---
    # Check if admin exists
    if not get_user('admin'):
        # Create default admin
        # Username: admin
        # Password: Admin123
        # Secret: JBSWY3DPEHPK3PXP (Standard base32 secret for testing)
        
        hardcoded_pass = "Admin123."
        hardcoded_secret = "JBSWY3DPEHPK3PXP" 
        
        hashed = auth.hash_password(hardcoded_pass)
        
        if add_user('admin', hashed, hardcoded_secret, role='admin'):
            add_log('SYSTEM', "INIT_ADMIN", "Created default admin user.")
            print("Default Admin Created: admin / Admin123")

def add_log(username, action, details=""):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (username, action, details) VALUES (?, ?, ?)",
            (username, action, details)
        )
        conn.commit()

def get_logs():
    with get_db() as conn:
        return pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", conn)

# --- User Operations ---
# Updated to support 'role' (default 'user')
def add_user(username, password_hash, totp_secret, role='user'):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if role column exists, if not add it (Migration)
            cursor.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'role' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
                
            cursor.execute(
                "INSERT INTO users (username, password_hash, totp_secret, role) VALUES (?, ?, ?, ?)",
                (username, password_hash, totp_secret, role)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def get_user(username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

# --- Inventory Operations ---
def add_item(name, category, quantity, price, description):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory (name, category, quantity, price, description) VALUES (?, ?, ?, ?, ?)",
            (name, category, quantity, price, description)
        )
        conn.commit()

def get_items():
    with get_db() as conn:
        return pd.read_sql_query("SELECT * FROM inventory", conn)

def update_item(item_id, name, category, quantity, price, description):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE inventory 
            SET name = ?, category = ?, quantity = ?, price = ?, description = ?
            WHERE id = ?
        ''', (name, category, quantity, price, description, item_id))
        conn.commit()

def delete_item(item_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
