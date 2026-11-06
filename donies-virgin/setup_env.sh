#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "    DONIES VIRGIN — Automated Environment Setup Script   "
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python & Create Virtualenv
echo "🐍 Setting up Python 3 virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Created .venv"
fi
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✅ Python dependencies installed."

# 2. Setup Remotion (Node.js)
echo "⚛️ Setting up Remotion dependencies..."
if [ -d "remotion" ]; then
    cd remotion
    if command -v npm &> /dev/null; then
        npm install
        echo "✅ Remotion npm packages installed."
    else
        echo "⚠️ npm not found. Please install Node.js 22 LTS to enable Remotion."
    fi
    cd "$SCRIPT_DIR"
fi

# 3. Setup Config and Environment file
if [ ! -f "config/.env" ] && [ -f "config/.env.example" ]; then
    cp config/.env.example config/.env
    echo "📄 Created config/.env from template."
fi

# 4. Initialize Database
echo "🐘 Initializing Virgin database schemas..."
python3 database/init_virgin_db.py

# 5. Run Verification Suite
echo "🧪 Running Parity & Isolation verification suite..."
python3 tests/test_virgin_parity.py

echo ""
echo "🎉 Donies Virgin environment setup complete and verified!"
echo "To activate python environment: source donies-virgin/.venv/bin/activate"
