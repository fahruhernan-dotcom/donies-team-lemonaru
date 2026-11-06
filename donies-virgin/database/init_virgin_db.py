#!/usr/bin/env python3
"""
DONIES VIRGIN — Database Initializer
Creates the isolated PostgreSQL tables and SQLite Swarm Matrix for the Virgin team.
Never touches or alters any existing doniesdaily_* production tables.
"""

import sys
import os
import sqlite3
import subprocess
from pathlib import Path

def init_postgres():
    print("🐘 Initializing PostgreSQL Virgin Schema...")
    sql_path = Path(__file__).parent / "virgin_schema.sql"
    if not sql_path.exists():
        print(f"❌ SQL file not found: {sql_path}")
        return False
    
    cmd = [
        "docker", "exec", "-i", "supabase-db",
        "psql", "-U", "postgres", "-d", "postgres"
    ]
    try:
        proc = subprocess.run(cmd, input=sql_path.read_text(encoding="utf-8"), text=True, capture_output=True, check=True)
        print("✅ PostgreSQL Virgin tables created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run psql: {e.stderr}")
        return False

def init_sqlite():
    print("🐝 Initializing SQLite Virgin Swarm Matrix...")
    db_path = Path(__file__).parents[1] / "data" / "virgin_virgin_agents_chat.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS agent_messages (
        id TEXT PRIMARY KEY,
        sender_id TEXT NOT NULL,
        sender_name TEXT NOT NULL,
        sender_avatar TEXT,
        sender_role TEXT,
        recipient_id TEXT DEFAULT 'all',
        recipient_name TEXT DEFAULT 'All Agents',
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        channel TEXT DEFAULT 'virgin_studio',
        status TEXT DEFAULT 'delivered',
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );

    CREATE TABLE IF NOT EXISTS agent_traces (
        id TEXT PRIMARY KEY,
        message_id TEXT NOT NULL REFERENCES agent_messages(id) ON DELETE CASCADE,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'none',
        content TEXT,
        icon TEXT,
        timestamp TEXT,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );

    CREATE INDEX IF NOT EXISTS idx_agent_messages_channel ON agent_messages(channel);
    CREATE INDEX IF NOT EXISTS idx_agent_messages_timestamp ON agent_messages(timestamp);
    CREATE INDEX IF NOT EXISTS idx_agent_traces_message_id ON agent_traces(message_id);
    """)
    conn.commit()
    conn.close()
    print(f"✅ SQLite Virgin Swarm Matrix initialized at {db_path}!")
    return True

if __name__ == "__main__":
    pg_ok = init_postgres()
    sq_ok = init_sqlite()
    if pg_ok and sq_ok:
        print("\n🎉 Virgin Database Environment 100% Ready and Isolated!")
    else:
        sys.exit(1)
