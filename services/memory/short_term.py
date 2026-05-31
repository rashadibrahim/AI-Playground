import time
from typing import List, Dict
import sqlite3
from ..summarizer.summarizer import Summarizer

class ShortTermMemory:
    def __init__(self, session_id: str, session_name: str, max_messages: int = 10, enable_summarization: bool = False):
        self.max_messages = max_messages
        self.enable_summarization = enable_summarization
        self.session_id = session_id
        self.session_name = session_name
        self.summarizer = Summarizer()
        self.history: List[Dict] = []
        self.conn = sqlite3.connect("./databases/short_term.db", check_same_thread=False)
        self._init_memory()

    def _init_memory(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                session_name TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL
            )
        """)
        self.conn.commit() 
        
        if self.enable_summarization:
            cursor = self.conn.cursor()
            cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (self.session_id,))
            rows = cursor.fetchmany(self.max_messages)
            if len(rows) > 0:
                for row in rows:
                    if row[0] == "summary":
                        self.history.clear()
                    self.history.append({"role": row[0], "content": row[1]})
                


    def add_message(self, role: str, content: str):
        self.conn.execute(
            "INSERT INTO messages (session_id, session_name, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (self.session_id, self.session_name, role, content, time.time())
        )
        self.conn.commit()
        if self.enable_summarization:
            self.history.append({"role": role, "content": content})
            if len(self.history) >= self.max_messages:
                if role == "assistant":
                    self._summarize_history()
                self.history.pop(0)
    
    def _summarize_history(self):
        last_summary_index = [i for i, msg in enumerate(self.history) if msg["role"] == "summary"]
        if len(last_summary_index) > 0:
            last_summary_index = last_summary_index[-1]
            if last_summary_index <= 1:
                messages_to_summarize = self.history[last_summary_index + 1:]
                summary = self.summarizer.summarize_conversation(messages_to_summarize)
                self.add_message("summary", summary)
        else:
            messages_to_summarize = self.history
            summary = self.summarizer.summarize_conversation(messages_to_summarize)
            self.add_message("summary", summary)
        
    
    def clear(self):
        self.conn.execute("DELETE FROM messages WHERE session_id = ?", (self.session_id,))
        self.conn.commit()
        self.history = []