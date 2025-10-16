#!/bin/bash
# Quick Start Script for BARD-RECO on Linux/Mac
# ==============================================

echo ""
echo "========================================"
echo "   BARD-RECO - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "[1/3] Checking Python installation..."
python3 --version

echo ""
echo "[2/3] Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo ""
echo "[3/3] Starting BARD-RECO..."
echo ""
echo "========================================"
echo "   Application starting..."
echo "   Default login: admin / admin123"
echo "   URL: http://localhost:8501"
echo "========================================"
echo ""

streamlit run app.py
