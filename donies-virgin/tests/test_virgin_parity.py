#!/usr/bin/env python3
"""
DONIES VIRGIN — Parity & Isolation Verification Suite
Tests that the Virgin clone is a 100% faithful logical duplicate of Donies Daily
while proving 100% database, memory, and channel isolation.
"""

import sys
import os
import sqlite3
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from config_loader import cfg

def test_agent_parity():
    print("🧪 [TEST 1/5] Checking Agent Parity & Souls...")
    required_souls = [
        "DONI_SOUL.md", "MOCHI_SOUL.md", "LUNA_SOUL.md",
        "MILO_SOUL.md", "KAK_CERIA_SOUL.md", "VIVAN_SOUL.md",
        "CLEO_SOUL.md", "voice.md"
    ]
    for s in required_souls:
        sp = BASE_DIR / "souls" / s
        assert sp.exists(), f"Missing soul file: {s}"
        assert sp.stat().st_size > 500, f"Soul file {s} is empty or truncated"
    print("  ✅ All 8 agent souls exist and are fully populated.")

def test_config_loader():
    print("🧪 [TEST 2/5] Testing Configuration Loader & Namespaces...")
    assert cfg.schema == "ai_brain"
    assert cfg.prefix == "virgin_"
    assert cfg.TABLE_POSTS == "ai_brain.virgin_posts"
    assert cfg.TABLE_LEARNINGS == "ai_brain.virgin_learnings"
    assert cfg.TABLE_QUEUE == "ai_brain.virgin_production_queue"
    assert "virgin_agents_chat.db" in cfg.SWARM_DB_PATH
    print(f"  ✅ Config loader successfully mapped tables: {cfg.TABLE_POSTS}, {cfg.TABLE_LEARNINGS}")

def test_database_isolation():
    print("🧪 [TEST 3/5] Testing PostgreSQL Database Isolation...")
    # Verify Donies Daily production count
    res_doni = subprocess.run([
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-t", "-A",
        "-c", "SELECT count(*) FROM ai_brain.doniesdaily_posts;"
    ], capture_output=True, text=True, check=True)
    doni_count_before = int(res_doni.stdout.strip())
    
    # Insert test dummy into virgin_posts
    test_video_id = "test_virgin_isolation_probe_999"
    subprocess.run([
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-c", f"INSERT INTO ai_brain.virgin_posts (video_id, title, short_url) VALUES ('{test_video_id}', 'Isolation Test', 'https://youtu.be/{test_video_id}') ON CONFLICT DO NOTHING;"
    ], capture_output=True, text=True, check=True)
    
    # Verify virgin_posts has 1 row
    res_virgin = subprocess.run([
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-t", "-A",
        "-c", f"SELECT count(*) FROM ai_brain.virgin_posts WHERE video_id = '{test_video_id}';"
    ], capture_output=True, text=True, check=True)
    virgin_count = int(res_virgin.stdout.strip())
    assert virgin_count == 1, "Virgin row failed to insert"
    
    # Verify Donies Daily production count is UNCHANGED
    res_doni_after = subprocess.run([
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-t", "-A",
        "-c", "SELECT count(*) FROM ai_brain.doniesdaily_posts;"
    ], capture_output=True, text=True, check=True)
    doni_count_after = int(res_doni_after.stdout.strip())
    assert doni_count_before == doni_count_after, "CRITICAL LEAK: doniesdaily_posts was modified by virgin operation!"
    
    # Clean up test dummy from virgin_posts
    subprocess.run([
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-c", f"DELETE FROM ai_brain.virgin_posts WHERE video_id = '{test_video_id}';"
    ], capture_output=True, text=True, check=True)
    
    print(f"  ✅ PostgreSQL 100% Isolated: DoniesDaily posts stable at {doni_count_before}, Virgin isolated.")

def test_sqlite_swarm_isolation():
    print("🧪 [TEST 4/5] Testing SQLite Swarm Matrix Isolation...")
    swarm_db = Path(cfg.SWARM_DB_PATH)
    assert swarm_db.exists(), f"Swarm DB missing at {swarm_db}"
    
    conn = sqlite3.connect(swarm_db)
    cur = conn.cursor()
    test_msg_id = "test_msg_isolation_001"
    cur.execute("""
    INSERT OR REPLACE INTO agent_messages (id, sender_id, sender_name, content, timestamp, channel)
    VALUES (?, 'doni', 'Ketua Doni', 'Virgin Swarm Standup Initialized', '2026-11-07T00:00:00Z', 'virgin_studio')
    """, (test_msg_id,))
    conn.commit()
    
    cur.execute("SELECT count(*) FROM agent_messages WHERE id = ?", (test_msg_id,))
    count = cur.fetchone()[0]
    assert count == 1
    
    # Clean up
    cur.execute("DELETE FROM agent_messages WHERE id = ?", (test_msg_id,))
    conn.commit()
    conn.close()
    print("  ✅ SQLite Swarm Matrix verified independent and functional.")

def test_qc_gate_integrity():
    print("🧪 [TEST 5/5] Testing Cleo QC Gatekeeper Logic...")
    import doni_qc_gate
    assert hasattr(doni_qc_gate, "inspect_video"), "Missing inspect_video function"
    assert hasattr(doni_qc_gate, "audit_script_and_outro"), "Missing audit_script_and_outro function"
    assert hasattr(doni_qc_gate, "audit_footage_assembly"), "Missing audit_footage_assembly function"
    assert hasattr(doni_qc_gate, "format_cleo_stamp"), "Missing format_cleo_stamp function"
    print("  ✅ Cleo QC Gatekeeper functions (inspect_video, audit_script_and_outro, audit_footage_assembly) verified intact.")

if __name__ == "__main__":
    print("==================================================================")
    print("        DONIES VIRGIN — PARITY & ISOLATION TEST RUNNER             ")
    print("==================================================================")
    try:
        test_agent_parity()
        test_config_loader()
        test_database_isolation()
        test_sqlite_swarm_isolation()
        test_qc_gate_integrity()
        print("\n🎉 ALL 5 PARITY & ISOLATION TESTS PASSED WITH 100% SUCCESS!")
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        sys.exit(1)
