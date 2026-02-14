#!/usr/bin/env python3
"""
Run the bot test from workspace directory
"""

import os
import sys

# Add polymarket_bot to path
bot_dir = os.path.join(os.path.dirname(__file__), 'polymarket_bot')
sys.path.append(bot_dir)

# Change to bot directory temporarily
original_dir = os.getcwd()
os.chdir(bot_dir)

try:
    # Import and run test
    from test_bot import main
    main()
finally:
    # Change back
    os.chdir(original_dir)