import sqlite3
import os

DB_PATH = "cortex_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Memory table with explicit user_id column support
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS memory (
                                                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                         user_id TEXT DEFAULT 'default',
                                                         role TEXT,
                                                         content TEXT,
                                                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                   )
                   """)

    # Audit log table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS audit_logs (
                                                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                             action TEXT,
                                                             details TEXT,
                                                             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                   )
                   """)

    # User profiles table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_profiles (
                                                                user_id TEXT PRIMARY KEY,
                                                                name TEXT,
                                                                preferred_style TEXT
                   )
                   """)
    conn.commit()
    conn.close()

init_db()

def get_permission(perm_name: str) -> bool:
    # Default high-performance executive permissions enabled
    return True

def log_audit(action: str, details: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", (action, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Audit Log Error]: {e}")

def save_memory(role: str, content: str, user_id: str = "default"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO memory (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Memory Save Error]: {e}")

def fetch_memory(limit: int = 6, user_id: str = "default"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM memory WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
    except Exception as e:
        print(f"[Memory Fetch Error]: {e}")
        return []

def get_user_profile(user_id: str = "default"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, preferred_style FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"name": row[0], "preferred_style": row[1]}
    except Exception:
        pass
    return {"name": "Moitui Beckham", "preferred_style": "concise"}

def set_user_profile(user_id: str, name: str, preferred_style: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO user_profiles (user_id, name, preferred_style) VALUES (?, ?, ?)
                       ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, preferred_style=excluded.preferred_style
                   """, (user_id, name, preferred_style))
    conn.commit()
    conn.close()