# filepath: webhook_receiver.py
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

class Commit(BaseModel):
    added: list[str] = []
    modified: list[str] = []
    removed: list[str] = []

class WebhookPayload(BaseModel):
    commits: list[Commit] = []

@app.post("/webhook")
async def handle_webhook(payload: WebhookPayload):
    # Get changed files from the webhook payload
    changed_files = set()
    for commit in payload.commits:
        changed_files.update(commit.added)
        changed_files.update(commit.modified)
        changed_files.update(commit.removed)
    
    # Check our specific files
    change_a = "Yes" if "a.yaml" in changed_files else "No"
    change_b = "Yes" if "b.yaml" in changed_files else "No"
    
    # Store in database
    conn = sqlite3.connect('changes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_changes (
            timestamp TEXT,
            change_a TEXT,
            change_b TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO file_changes (timestamp, change_a, change_b)
        VALUES (?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), change_a, change_b))
    conn.commit()
    conn.close()
    
    return {"status": "success"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=2714)