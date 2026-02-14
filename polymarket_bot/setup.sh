#!/bin/bash
# Setup script for Polymarket Trading Bot

echo "=========================================="
echo "Polymarket Trading Bot Setup"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required"; exit 1; }

# Create virtual environment (optional but recommended)
echo -n "Create virtual environment? (y/n): "
read create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "=========================================="
    echo "IMPORTANT: Edit .env file with your credentials"
    echo "=========================================="
    echo ""
    echo "1. Get your private key from:"
    echo "   https://reveal.magic.link/polymarket"
    echo ""
    echo "2. Get your funder address from:"
    echo "   polymarket.com/settings → Wallet"
    echo ""
    echo "3. Make at least one manual trade on polymarket.com"
    echo "   (This activates API permissions)"
    echo ""
    echo "4. Edit .env and add:"
    echo "   POLYMARKET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY"
    echo "   POLYMARKET_FUNDER_ADDRESS=0xYOUR_ADDRESS"
    echo ""
    read -p "Press Enter when you've edited .env..."
fi

# Test the setup
echo "Testing setup..."
python test_bot.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To run the bot:"
echo "  python main.py"
echo ""
echo "Options:"
echo "  1. Run once (immediate)"
echo "  2. Run scheduled (every 30 minutes)"
echo "  3. Test components only"
echo ""
echo "Start with option 3 to verify everything works!"
echo ""