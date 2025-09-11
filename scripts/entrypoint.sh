#!/usr/bin/env bash
set -e

echo "🚀 Starting CoolBits.ai Docker container..."

# Create necessary directories
mkdir -p data logs

echo "📁 Created data and logs directories"

# Initialize database
echo "🗄️ Initializing database..."
python -c "from app.core.db import create_tables; create_tables()"

# Seed users
echo "👥 Seeding users..."
python -m app.seed.seed_users

echo "✅ Database setup complete!"

# Start Streamlit
echo "🌐 Starting Streamlit server..."
exec streamlit run coolbits_web_app.py --server.port 8501 --server.address 0.0.0.0
