-- Schema for SQLite Swarm Matrix (agents_chat.db)

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
    channel TEXT DEFAULT 'all',
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
