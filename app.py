"""
app.py - Root Entrypoint for CyberBreach Intel Dashboard
Author: Cybersecurity Analytics Team
Usage:
    python app.py
"""

import sys
import os

# Ensure workspace root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dashboard.app import app, server, run_dashboard

if __name__ == '__main__':
    # Launch on default port 8050
    run_dashboard(host='127.0.0.1', port=8050, debug=False)
