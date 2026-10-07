"""
config.py - Application Configuration, Data Loading & Palette Definitions
Author: Cybersecurity Analytics Team
"""

import os
import pandas as pd

# Base Directory Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CLEANED_DATA_PATH = os.path.join(DATA_DIR, 'cleaned_breach_data.csv')
CLASSES_DATA_PATH = os.path.join(DATA_DIR, 'breach_data_classes.csv')
DB_PATH = os.path.join(DATA_DIR, 'breaches.db')

# Enterprise Light Theme Color System
THEME = {
    'bg_main': '#F8FAFC',
    'bg_card': '#FFFFFF',
    'navy': '#0F172A',
    'violet': '#6D28D9',
    'violet_hover': '#5B21B6',
    'blue': '#1D4ED8',
    'light_violet': '#EDE9FE',
    'muted': '#64748B',
    'border': '#E2E8F0',
    'border_subtle': '#F1F5F9',
    'teal': '#0D9488',
    'amber': '#D97706',
    'red': '#DC2626'
}

IMPACT_COLORS = {
    'Critical': '#DC2626',
    'High': '#EA580C',
    'Medium': '#D97706',
    'Low': '#16A34A'
}

PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': '#FFFFFF',
        'plot_bgcolor': '#FFFFFF',
        'font': {'family': 'Segoe UI, -apple-system, sans-serif', 'color': THEME['navy']},
        'margin': {'l': 40, 'r': 20, 't': 40, 'b': 40},
        'xaxis': {
            'gridcolor': '#F1F5F9',
            'linecolor': THEME['border'],
            'tickfont': {'size': 11, 'color': THEME['muted']},
            'titlefont': {'size': 12, 'color': THEME['navy'], 'family': 'Segoe UI'}
        },
        'yaxis': {
            'gridcolor': '#F1F5F9',
            'linecolor': THEME['border'],
            'tickfont': {'size': 11, 'color': THEME['muted']},
            'titlefont': {'size': 12, 'color': THEME['navy'], 'family': 'Segoe UI'}
        }
    }
}

def load_data():
    """Load cleaned datasets once at application boot."""
    if not os.path.exists(CLEANED_DATA_PATH):
        raise FileNotFoundError(f"Cleaned dataset not found at {CLEANED_DATA_PATH}. Please run analysis/02_data_cleaning.py first.")
    
    df = pd.read_csv(CLEANED_DATA_PATH)
    df_classes = pd.read_csv(CLASSES_DATA_PATH)
    
    # Ensure types
    df['BreachDate'] = pd.to_datetime(df['BreachDate'], errors='coerce')
    df['AddedDate'] = pd.to_datetime(df['AddedDate'], errors='coerce')
    df['ModifiedDate'] = pd.to_datetime(df['ModifiedDate'], errors='coerce')
    df['PwnCount'] = pd.to_numeric(df['PwnCount'], errors='coerce').fillna(0).astype('int64')
    
    return df, df_classes

def format_compact(num):
    """Format large numbers into clean human-readable representations (e.g. 1.2M, 500K)."""
    if num is None or pd.isna(num):
        return "0"
    num = float(num)
    if abs(num) >= 1e9:
        return f"{num / 1e9:.2f}B"
    elif abs(num) >= 1e6:
        return f"{num / 1e6:.2f}M"
    elif abs(num) >= 1e3:
        return f"{num / 1e3:.1f}K"
    else:
        return f"{num:,.0f}"

def format_full(num):
    """Format integers with commas."""
    if num is None or pd.isna(num):
        return "0"
    return f"{int(num):,}"
