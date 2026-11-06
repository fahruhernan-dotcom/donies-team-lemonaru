import sys
import os
import json
import time
import urllib.request
from pathlib import Path
from audit_context import get_complete_knowledge_context

AUDIT_DIR = Path("/home/ubuntu/donies_daily_master_audit")
PROXY_URL = "http://127.0.0.1:8317/v1/chat/completions"
MODEL_NAME = "gemini-4-argon-high"

SYSTEM_PROMPT = """You are a Principal AI Systems Architect, Agentic Workflow Engineer, and Reverse Engineering Specialist.
You are conducting a formal, evidence-based MASTER SYSTEM AUDIT of the DONIES DAILY autonomous multi-agent production ecosystem.
You are given the COMPLETE verified raw context, code, schemas, souls, and logs of the system.

STRICT OPERATING RULES:
1. READ-ONLY AUDIT. Understand and document reality before recommending changes.
2. Ground every single claim, metric, path, agent role, and mechanism in the provided evidence.
3. No hallucination. If a component is planned or unverified, state it explicitly as UNVERIFIED or PARTIALLY IMPLEMENTED.
4. Output must be professional, highly technical, exhaustive, well-structured Markdown. Do not summarize or cut corners.
5. Provide comprehensive tables, diagrams (using Mermaid), precise file paths, and code snippets where relevant.
"""

def call_argon(prompt: str, context: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"=== RAW VERIFIED SYSTEM CONTEXT & EVIDENCE ===\n{context}\n\n=== AUDIT TASK INSTRUCTION ===\n{prompt}"}
        ],
        "temperature": 0.2
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        PROXY_URL,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": "Bearer cpa-secret-key-12345"}
    )
    # Retry loop up to 3 attempts
    for attempt in range(1, 4):
        try:
            print(f"Calling {MODEL_NAME} (attempt {attempt}/3)...", flush=True)
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=300) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                content = res["choices"][0]["message"]["content"]
                elapsed = time.time() - t0
                print(f"Success in {elapsed:.1f}s ({len(content)} chars)", flush=True)
                return content
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}", file=sys.stderr, flush=True)
            time.sleep(5)
    raise RuntimeError(f"Failed to call {MODEL_NAME} after 3 attempts.")

if __name__ == "__main__":
    print("Audit generator module loaded successfully.")
