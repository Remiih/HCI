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

def init_db():
    """Initialize the database tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                totp_secret TEXT NOT NULL
            )
        ''')
        
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
def add_user(username, password_hash, totp_secret):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, totp_secret) VALUES (?, ?, ?)",
                (username, password_hash, totp_secret)
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
