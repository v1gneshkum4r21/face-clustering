import sqlite3
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = Path("requests.db")
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    request_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    cluster_id TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            ''')
    
    def create_request(self, request_id, email, cluster_id, image_path, status='pending'):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute('''
                INSERT INTO requests 
                (request_id, email, cluster_id, image_path, status, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request_id, email, cluster_id, image_path, status, datetime.now()))
    
    def get_pending_requests(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM requests WHERE status = "pending" ORDER BY submitted_at DESC')
            return cursor.fetchall()
    
    def update_request_status(self, request_id, status):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE requests SET status = ? WHERE request_id = ?', (status, request_id))
            conn.commit()
    
    def get_request_by_id(self, request_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM requests WHERE request_id = ?', (request_id,))
            return cursor.fetchone()
    
    def get_all_requests(self, status=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    'SELECT * FROM requests WHERE status = ? ORDER BY submitted_at DESC',
                    (status,)
                )
            else:
                cursor.execute('SELECT * FROM requests ORDER BY submitted_at DESC')
            return cursor.fetchall()
    
    def get_request_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    status, 
                    COUNT(*) as count 
                FROM requests 
                GROUP BY status
            ''')
            return dict(cursor.fetchall())
