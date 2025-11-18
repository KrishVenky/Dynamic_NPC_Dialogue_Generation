#!/bin/bash
# Quick Start Script for NPC Dialogue Generator

echo "🚀 Starting NPC Dialogue Generator Setup..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies (this may take a few minutes)..."
pip install --quiet flask flask-cors python-dotenv pandas transformers torch sentence-transformers chromadb

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    echo "HF_TOKEN=" > .env
    echo "PORT=3000" >> .env
    echo "✅ .env file created. Edit it if you have a HuggingFace token (optional)."
else
    echo "✅ .env file found."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 To start the server:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "📖 Then open: http://localhost:3000"
echo ""
