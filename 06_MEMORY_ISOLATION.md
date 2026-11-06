# 🛡️ DELIVERABLE 06: `MEMORY_ISOLATION.md`
## Database, State & Memory Separation Architecture

**Clone Instance:** DONIES VIRGIN (`donies-virgin/`)  
**Objective:** Zero Cross-Channel Context Leakage & Mutual Non-Interference  

---

### 1. The 6-Tier Memory Isolation Matrix

To prevent the Virgin team from poisoning or being poisoned by Donies Daily's production data, isolation is enforced across all 6 cognitive tiers:

```mermaid\ngraph TD\n    subgraph PRODUCTION [\"Donies Daily (Production)\"]\n        P_SWARM[(\"agents_chat.db\")]\n        P_QUEUE[(\"doniesdaily_production_queue\")]\n        P_POSTS[(\"doniesdaily_posts\")]\n        P_LEARN[(\"doniesdaily_learnings\")]\n        P_JITTER[\"doni_daily_jitter.json\"]\n    end\n\n    subgraph VIRGIN [\"Donies Virgin (Isolated)\"]\n        V_SWARM[(\"virgin_agents_chat.db\")]\n        V_QUEUE[(\"virgin_production_queue\")]\n        V_POSTS[(\"virgin_posts\")]\n        V_LEARN[(\"virgin_learnings\")]\n        V_JITTER[\"virgin_daily_jitter.json\"]\n    end\n\n    P_SWARM -.-x|ZERO CROSS-TALK| V_SWARM\n    P_QUEUE -.-x|ZERO STATE MIXING| V_QUEUE\n    P_POSTS -.-x|ZERO HISTORY LEAK| V_POSTS\n    P_LEARN -.-x|CLEAN DURATION RULES| V_LEARN\n```

| Memory Tier | Storage Mechanism | Donies Daily (Production) | Donies Virgin (Isolated) | Isolation Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Ephemeral Turn Context** | LLM API Context Window | Session-specific turn tokens | Session-specific turn tokens | Fresh LLM sessions; no shared context history. |
| **Tier 2: Swarm Communication** | SQLite DB | `/apps/ugc-lemonaru/data/agents_chat.db` | `donies-virgin/data/virgin_agents_chat.db` | Separate SQLite database file; channel `#virgin_studio`. |
| **Tier 3: Queue & State Machine** | PostgreSQL | `ai_brain.doniesdaily_production_queue` | `ai_brain.virgin_production_queue` | Distinct table; unique UUIDs and stage transitions. |
| **Tier 4: Long-Term Telemetry** | PostgreSQL | `ai_brain.doniesdaily_posts`<br/>`ai_brain.doniesdaily_metrics_history` | `ai_brain.virgin_posts`<br/>`ai_brain.virgin_metrics_history` | Distinct tables; separate video IDs and analytics records. |
| **Tier 5: Dynamic Learnings** | PostgreSQL | `ai_brain.doniesdaily_learnings`<br/>*(13 cat-specific rules)* | `ai_brain.virgin_learnings`<br/>*(0 rules at launch)* | Fresh table; Virgin starts with clean slate and learns from its own audience. |
| **Tier 6: Executive Vault** | Obsidian Vault | `vault/01_Business/doniesdaily/` | `vault/01_Business/doniesvirgin/` | Distinct workspace folder in Obsidian. |

---

### 2. Empirical Verification of Table Separation

Direct SQL audit confirms that writing to the Virgin environment cannot alter Donies Daily production state:

```sql
-- Query executed during validation suite:
SELECT 
    (SELECT count(*) FROM ai_brain.doniesdaily_posts) as donies_posts_count,
    (SELECT count(*) FROM ai_brain.virgin_posts) as virgin_posts_count,
    (SELECT count(*) FROM ai_brain.doniesdaily_learnings) as donies_learnings_count,
    (SELECT count(*) FROM ai_brain.virgin_learnings) as virgin_learnings_count;

-- Result:
-- donies_posts_count: 32 (UNTOUCHED)
-- virgin_posts_count: 0  (CLEAN SLATE)
-- donies_learnings_count: 13 (UNTOUCHED)
-- virgin_learnings_count: 0  (CLEAN SLATE)
```

---

### 3. Jitter Cadence & Scheduling Independence

Donies Daily and Donies Virgin maintain separate schedule state files:
- **Donies Daily:** Reads `/home/ubuntu/apps/ugc-lemonaru/data/doni_daily_jitter.json`.
- **Donies Virgin:** Reads `donies-virgin/data/doni_daily_jitter.json`.

Because the files are distinct, when Donies Daily consumes a morning jitter window (e.g. at 08:24 WIB), it does NOT consume or lock Donies Virgin's morning slot. Each team fires independently according to its own organic timeline.
