import sqlite3
import subprocess
from datetime import datetime
import os

def get_changed_files():
    try:
        # This command compares the current commit to the previous one
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.splitlines()
    except Exception:
        return []

def update_db():
    changed_files = get_changed_files()
    
    # Check if our specific files were in the list of changed files
    change_a = "Yes" if "a.yaml" in changed_files else "No"
    change_b = "Yes" if "b.yaml" in changed_files else "No"
    
    # Connect to SQLite
    conn = sqlite3.connect('changes.db')
    cursor = conn.cursor()
    
    # Create the table if this is the first time running
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_changes (
            timestamp TEXT,
            change_a TEXT,
            change_b TEXT
        )
    ''')
    
    # Add the new log entry
    cursor.execute('''
        INSERT INTO file_changes (timestamp, change_a, change_b)
        VALUES (?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), change_a, change_b))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_db()