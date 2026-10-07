"""
app.py - Dash Application Factory & App Engine
Author: Cybersecurity Analytics Team
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from dashboard.config import load_data, THEME
from dashboard.layout import create_header, create_global_filter_bar, render_overview_page
from dashboard.callbacks import register_callbacks

# Load datasets once into memory
df, df_classes = load_data()

# Initialize Dash application with clean Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="CyberBreach Intel | Data Breach Analytics Platform"
)

server = app.server

# Global Application Layout
app.layout = html.Div([
    # Client-side state storage
    dcc.Store(id='store-active-page', data='overview'),
    dcc.Store(id='store-filtered-indices', data=df.index.tolist()),

    # Header & Global Filter Bar
    create_header(),
    create_global_filter_bar(df),

    # Dynamic Page Container
    dbc.Container([
        html.Div(id='page-content', children=render_overview_page(df))
    ], fluid=True, className="pb-5"),

    # Enterprise Footer
    html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Span("CYBERBREACH INTEL PLATFORM", style={'fontWeight': '700', 'color': THEME['navy'], 'fontSize': '0.8rem'}),
                    html.Span(" • Academic Research & Data Analytics Project", style={'color': THEME['muted'], 'fontSize': '0.75rem'}),
                    html.Div("Methodology: Rigorous dataset audit, statistical log-scaling, normalized 1:N data-classes parsing, and non-destructive cleaning.",
                             style={'color': THEME['muted'], 'fontSize': '0.7rem', 'marginTop': '2px'})
                ], md=8, xs=12),
                dbc.Col([
                    html.Div([
                        html.Span("Corpus Records: ", style={'fontSize': '0.75rem', 'color': THEME['muted']}),
                        html.Strong(f"{len(df):,} breaches", style={'fontSize': '0.75rem', 'color': THEME['violet']}),
                        html.Span(" | Accounts: ", style={'fontSize': '0.75rem', 'color': THEME['muted']}),
                        html.Strong(f"{df['PwnCount'].sum():,}", style={'fontSize': '0.75rem', 'color': THEME['blue']})
                    ], className="text-md-end mt-2 mt-md-0")
                ], md=4, xs=12)
            ])
        ], fluid=True)
    ], style={'backgroundColor': '#FFFFFF', 'borderTop': f'1px solid {THEME["border"]}', 'padding': '1rem 0', 'marginTop': 'auto'})
], style={'minHeight': '100vh', 'display': 'flex', 'flexDirection': 'column'})

# Register all interactive callbacks
register_callbacks(app, df, df_classes)

def run_dashboard(host='127.0.0.1', port=8050, debug=False):
    """Launch dashboard locally on specified host and port."""
    print("=" * 65)
    print("  CYBERBREACH INTEL - DATA BREACH INTELLIGENCE DASHBOARD")
    print("=" * 65)
    print(f"  [+] Active Database: {len(df):,} breaches loaded")
    print(f"  [+] Total Compromised Accounts: {df['PwnCount'].sum():,}")
    print(f"  [+] Normalized DataClasses: {len(df_classes):,} relations")
    print(f"  [+] Server running at: http://{host}:{port}/")
    print("  [+] Press CTRL+C to stop the application")
    print("=" * 65)
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_dashboard()
