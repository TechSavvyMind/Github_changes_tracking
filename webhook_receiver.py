# filepath: webhook_receiver.py
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Get port from Railway environment variable or default to 8080
PORT = int(os.environ.get("PORT", 8080))

class Commit(BaseModel):
    added: list[str] = []
    modified: list[str] = []
    removed: list[str] = []

class WebhookPayload(BaseModel):
    commits: list[Commit] = []

@app.get("/")
async def root():
    return {"status": "running", "service": "github-webhook-receiver"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/webhook")
async def handle_webhook(payload: WebhookPayload):
    logger.info("Received webhook payload")
    
    # Get changed files from the webhook payload
    changed_files = set()
    for commit in payload.commits:
        changed_files.update(commit.added)
        changed_files.update(commit.modified)
        changed_files.update(commit.removed)
    
    logger.info(f"Changed files: {changed_files}")
    
    # Check our specific files
    change_a = "Yes" if "a.yaml" in changed_files else "No"
    change_b = "Yes" if "b.yaml" in changed_files else "No"
    
    logger.info(f"a.yaml: {change_a}, b.yaml: {change_b}")
    
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
    
    logger.info("Successfully recorded changes")
    return {"status": "success"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)