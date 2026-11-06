import json
import sqlite3
import subprocess
from pathlib import Path

def get_complete_knowledge_context() -> str:
    parts = []

    # 1. PRD Master Specs
    prd_path = Path("/home/ubuntu/apps/ugc-lemonaru/PRD_DONIESDAILY_MASTER_SPEC.md")
    if prd_path.exists():
        parts.append(f"### [SPECIFICATION] PRD_DONIESDAILY_MASTER_SPEC.md\n```markdown\n{prd_path.read_text(encoding='utf-8')}\n```\n")

    ingest_path = Path("/home/ubuntu/apps/ugc-lemonaru/PRD_FAHRU_FOOTAGE_INGESTION_SOP.md")
    if ingest_path.exists():
        parts.append(f"### [SPECIFICATION] PRD_FAHRU_FOOTAGE_INGESTION_SOP.md\n```markdown\n{ingest_path.read_text(encoding='utf-8')}\n```\n")

    # 2. Souls
    souls_dir = Path("/home/ubuntu/apps/ugc-lemonaru/souls")
    for sp in sorted(souls_dir.glob("*.md")):
        parts.append(f"### [AGENT SOUL] {sp.name}\n```markdown\n{sp.read_text(encoding='utf-8')}\n```\n")

    # 3. Active Context from Obsidian Vault
    vault_ctx = Path("/home/ubuntu/vault/01_Business/doniesdaily/ActiveContext.md")
    if vault_ctx.exists():
        parts.append(f"### [OBSIDIAN VAULT ACTIVE CONTEXT] ActiveContext.md\n```markdown\n{vault_ctx.read_text(encoding='utf-8')[:12000]}\n```\n")

    # 4. Postgres DB Schemas & Data
    tables = ['doniesdaily_sniper_logs', 'doniesdaily_content_ideas', 'doniesdaily_production_queue', 'doniesdaily_clip_usage', 'doniesdaily_learnings', 'doniesdaily_posts', 'doniesdaily_metrics_history']
    parts.append("### [POSTGRESQL AI_BRAIN TABLES & ACTIVE RULES]\n")
    for t in tables:
        cmd = ['docker', 'exec', 'supabase-db', 'psql', '-U', 'postgres', '-d', 'postgres', '-c', f'\\d ai_brain.{t}']
        res = subprocess.run(cmd, capture_output=True, text=True)
        parts.append(f"#### Table Schema: ai_brain.{t}\n```sql\n{res.stdout}\n```\n")

    # Active learnings
    cmd_l = ['docker', 'exec', 'supabase-db', 'psql', '-U', 'postgres', '-d', 'postgres', '-c', "SELECT id, category, rule_name, directive, confidence_score, status FROM ai_brain.doniesdaily_learnings;"]
    res_l = subprocess.run(cmd_l, capture_output=True, text=True)
    parts.append(f"#### Active Rules in ai_brain.doniesdaily_learnings:\n```text\n{res_l.stdout}\n```\n")

    # Cadence tasks
    cmd_c = ['docker', 'exec', 'supabase-db', 'psql', '-U', 'postgres', '-d', 'postgres', '-c', "SELECT task_key, title, cron_expr, action_type, action_payload, status FROM ai_brain.cadence_tasks WHERE business_unit = 'doniesdaily' OR task_key ILIKE '%doni%';"]
    res_c = subprocess.run(cmd_c, capture_output=True, text=True)
    parts.append(f"#### Cadence Tasks in ai_brain.cadence_tasks:\n```text\n{res_c.stdout}\n```\n")

    # 5. SQLite agents_chat.db Swarm Matrix
    conn = sqlite3.connect('/home/ubuntu/vps-control-center/backend/data/agents_chat.db')
    cur = conn.cursor()
    cur.execute("SELECT sender_id, sender_name, sender_role, channel, count(*) FROM agent_messages GROUP BY sender_id, sender_name, sender_role, channel;")
    msg_stats = cur.fetchall()
    parts.append(f"### [SWARM MATRIX SQLITE CHAT STATS]\n```json\n{json.dumps(msg_stats, indent=2)}\n```\n")

    cur.execute("SELECT sender_name, content, timestamp FROM agent_messages WHERE channel='donies' ORDER BY created_at DESC LIMIT 15;")
    recent_msgs = cur.fetchall()
    parts.append(f"#### Recent Swarm Messages in #donies:\n```text\n")
    for sender, content, ts in recent_msgs:
        parts.append(f"[{ts}] {sender}: {content[:200]}...\n")
    parts.append("```\n")
    conn.close()

    # 6. Core Python Scripts Summaries & Code Snippets
    scripts = [
        "/home/ubuntu/tools/doni_production_sprint.py",
        "/home/ubuntu/tools/doni_working_hours_standup.py",
        "/home/ubuntu/tools/doni_scriptwriter.py",
        "/home/ubuntu/apps/ugc-lemonaru/src/doni_remotion_flow_pipeline.py",
        "/home/ubuntu/apps/ugc-lemonaru/src/doni_qc_gate.py",
        "/home/ubuntu/apps/ugc-lemonaru/src/youtube_api_publisher.py",
    ]
    parts.append("### [CORE PIPELINE & ORCHESTRATION PYTHON CODE]\n")
    for s in scripts:
        sp = Path(s)
        if sp.exists():
            code = sp.read_text(encoding='utf-8')
            parts.append(f"#### File: {s} ({len(code)} bytes)\n```python\n{code[:8000]}\n```\n")

    # 7. Remotion Component Snippets
    rem_files = [
        "/home/ubuntu/apps/ugc-lemonaru/remotion/src/DoniOverlay.tsx",
        "/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/HookTitle.tsx",
        "/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/OutroCTA.tsx",
        "/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/StoryCoverCard.tsx",
    ]
    parts.append("### [REMOTION REACT COMPONENTS]\n")
    for rf in rem_files:
        rp = Path(rf)
        if rp.exists():
            parts.append(f"#### Component: {rf}\n```tsx\n{rp.read_text(encoding='utf-8')[:4000]}\n```\n")

    # 8. Catalog stats
    cat_path = Path("/home/ubuntu/apps/ugc-lemonaru/data/cat_assets_catalog.json")
    if cat_path.exists():
        with open(cat_path) as f:
            cat_data = json.load(f)
        parts.append(f"### [VIDEO ASSET CATALOG]\nTotal clips: {len(cat_data)}. Sample entry: {json.dumps(cat_data[0] if cat_data else {}, indent=2)}\n")

    return "\n".join(parts)

if __name__ == "__main__":
    ctx = get_complete_knowledge_context()
    print("Context compiled successfully! Total chars:", len(ctx))
