import sqlite3
import json
import time
from typing import Dict, Optional

class ParentStore:
    def __init__(self, db_path: str = "./databases/parent_docs.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_table()
    
    def _init_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS parents (
                parent_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at REAL
            )
        """)
        self.conn.commit()
    
    def save_parent(self, parent_id: str, content: str, metadata: Dict = None):
        self.conn.execute(
            "INSERT OR REPLACE INTO parents VALUES (?, ?, ?, ?)",
            (parent_id, content, json.dumps(metadata or {}), time.time())
        )
        self.conn.commit()
    
    def get_parent(self, parent_id: str) -> Optional[Dict]:
        cursor = self.conn.execute(
            "SELECT content, metadata FROM parents WHERE parent_id = ?", 
            (parent_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "content": row[0],
                "metadata": json.loads(row[1]) if row[1] else {}
            }
        return None