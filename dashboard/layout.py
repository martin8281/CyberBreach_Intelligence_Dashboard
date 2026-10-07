"""
layout.py - Multi-Page UI Layout for Cybersecurity Intelligence Platform
Author: Cybersecurity Analytics Team
"""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dashboard.config import THEME, IMPACT_COLORS

def create_header():
    """Top navigation bar with brand, page tabs, and live status badges."""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("🛡️", style={'fontSize': '1.6rem', 'marginRight': '0.5rem'}),
                        html.Div([
                            html.Span("CYBERBREACH", style={'color': THEME['violet'], 'fontWeight': '900', 'letterSpacing': '-0.02em', 'fontSize': '1.35rem'}),
                            html.Span("INTEL", style={'color': THEME['blue'], 'fontWeight': '900', 'letterSpacing': '-0.02em', 'fontSize': '1.35rem', 'marginLeft': '2px'}),
                            html.Span("ENTERPRISE PLATFORM", className="brand-badge", style={'marginLeft': '0.65rem'}),
                            html.Div("Cybersecurity Threat Intelligence & Data Breach Analytics",
                                     style={'fontSize': '0.75rem', 'color': THEME['muted'], 'marginTop': '-2px', 'fontWeight': '500'})
                        ])
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], md=5, xs=12, className="d-flex align-items-center mb-2 mb-md-0"),
                dbc.Col([
                    html.Div([
                        dbc.Nav([
                            dbc.NavLink("Executive Overview", id="tab-overview", active=True, href="#", className="me-1"),
                            dbc.NavLink("Breach Intelligence", id="tab-intelligence", active=False, href="#", className="me-1"),
                            dbc.NavLink("Entity Analysis", id="tab-entity", active=False, href="#", className="me-1"),
                            dbc.NavLink("Breach Explorer", id="tab-explorer", active=False, href="#")
                        ], pills=True, className="justify-content-md-end")
                    ])
                ], md=7, xs=12, className="d-flex justify-content-md-end align-items-center")
            ])
        ], fluid=True)
    ], className="app-navbar")

def create_global_filter_bar(df):
    """Global filtering panel applicable across analytical views."""
    min_year = int(df['BreachYear'].min())
    max_year = int(df['BreachYear'].max())

    return html.Div([
        dbc.Container([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Span("GLOBAL THREAT FILTERS", style={'fontWeight': '800', 'color': THEME['violet'], 'fontSize': '0.8rem', 'letterSpacing': '0.05em'}),
                                html.Span(" • Real-time Threat Intelligence Filter Pipeline", style={'color': THEME['muted'], 'fontSize': '0.75rem'})
                            ], className="mb-2")
                        ], xs=8),
                        dbc.Col([
                            html.Div([
                                dbc.Button("↺ Reset Filters", id="btn-reset-filters", size="sm", className="btn-reset float-end")
                            ])
                        ], xs=4)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Breach Year Range", className="filter-label"),
                            dcc.RangeSlider(
                                id='filter-year-range',
                                min=min_year,
                                max=max_year,
                                step=1,
                                value=[min_year, max_year],
                                marks={y: {'label': str(y), 'style': {'fontSize': '9px', 'color': THEME['muted']}}
                                       for y in range(min_year, max_year + 1, 3)},
                                tooltip={'placement': 'bottom', 'always_visible': False}
                            )
                        ], lg=4, md=6, xs=12, className="mb-3 mb-lg-0"),

                        dbc.Col([
                            html.Label("Impact Level Severity", className="filter-label"),
                            dcc.Dropdown(
                                id='filter-impact-level',
                                options=[{'label': "Critical (≥10M accounts)", 'value': 'Critical'},
                                         {'label': "High (1M - 10M accounts)", 'value': 'High'},
                                         {'label': "Medium (100K - 1M accounts)", 'value': 'Medium'},
                                         {'label': "Low (<100K accounts)", 'value': 'Low'}],
                                value=['Critical', 'High', 'Medium', 'Low'],
                                multi=True,
                                clearable=False
                            )
                        ], lg=3, md=6, xs=12, className="mb-3 mb-lg-0"),

                        dbc.Col([
                            html.Label("Verification Status", className="filter-label"),
                            dcc.Dropdown(
                                id='filter-verification',
                                options=[
                                    {'label': 'All Records', 'value': 'ALL'},
                                    {'label': 'Verified Only', 'value': 'VERIFIED'},
                                    {'label': 'Unverified Only', 'value': 'UNVERIFIED'}
                                ],
                                value='ALL',
                                clearable=False
                            )
                        ], lg=2, md=6, xs=12, className="mb-3 mb-lg-0"),

                        dbc.Col([
                            html.Label("Sensitivity Status", className="filter-label"),
                            dcc.Dropdown(
                                id='filter-sensitivity',
                                options=[
                                    {'label': 'All Privacy Levels', 'value': 'ALL'},
                                    {'label': 'Sensitive Only', 'value': 'SENSITIVE'},
                                    {'label': 'Standard Only', 'value': 'STANDARD'}
                                ],
                                value='ALL',
                                clearable=False
                            )
                        ], lg=3, md=6, xs=12)
                    ], className="align-items-center")
                ], className="p-3")
            ], className="filter-card mb-4")
        ], fluid=True)
    ])

def render_kpi_card(card_id, title, value, subtext, accent_color=THEME['violet']):
    return dbc.Col([
        html.Div([
            html.Div(title, className="kpi-title"),
            html.Div(value, id=f"kpi-val-{card_id}", className="kpi-value"),
            html.Div(subtext, id=f"kpi-sub-{card_id}", className="kpi-subtext")
        ], className="kpi-card", style={'--card-accent': accent_color})
    ], lg=3, md=6, xs=12, className="mb-3")

def render_overview_page(df):
    """PAGE 1: Executive Overview layout."""
    return html.Div([
        # Page Title & Subtitle
        html.Div([
            html.H2("Cybersecurity Data Breach Intelligence", style={'color': THEME['navy'], 'fontWeight': '800', 'marginBottom': '0.2rem'}),
            html.P("Enterprise Overview of Historical Data Breach Activity", style={'color': THEME['muted'], 'fontSize': '0.95rem', 'marginBottom': '1.25rem'})
        ]),

        # 8 KPI Cards
        dbc.Row([
            render_kpi_card("total-breaches", "Total Breaches", f"{len(df):,}", "Catalogued incidents", THEME['violet']),
            render_kpi_card("total-accounts", "Total Accounts Affected", "0", "Exposed identities", THEME['blue']),
            render_kpi_card("avg-size", "Average Breach Size", "0", "Mean accounts per breach", THEME['teal']),
            render_kpi_card("max-breach", "Largest Single Breach", "0", "Peak incident volume", THEME['red']),
        ]),
        dbc.Row([
            render_kpi_card("verified-breaches", "Verified Breaches", "0", "Authenticated records", THEME['teal']),
            render_kpi_card("sensitive-breaches", "Sensitive Breaches", "0", "High privacy risk", '#BE185D'),
            render_kpi_card("malware-breaches", "Malware-Associated Breaches", "0", "Botnet / stealer logs", '#B91C1C'),
            render_kpi_card("critical-breaches", "Critical + High Impact Breaches", "0", "Severe (≥1M accounts)", '#EA580C'),
        ], className="mb-2"),

        # Row 1: Charts
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("Annual Breach Frequency", className="chart-title"),
                        html.P("Year-by-year incident count and cumulative trajectory", className="chart-subtitle")
                    ], className="chart-header"),
                    dcc.Graph(id='chart-breaches-over-time', config={'displayModeBar': False})
                ], className="chart-card")
            ], lg=7, xs=12),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Accounts Affected by Year", className="chart-title"),
                            html.P("Compromised account volume with scale toggle", className="chart-subtitle")
                        ]),
                        dbc.RadioItems(
                            id='radio-account-scale',
                            options=[
                                {'label': 'Linear Scale', 'value': 'linear'},
                                {'label': 'Log Scale', 'value': 'log'}
                            ],
                            value='linear',
                            inline=True,
                            className="text-muted",
                            style={'fontSize': '0.75rem'}
                        )
                    ], className="chart-header"),
                    dcc.Graph(id='chart-accounts-over-time', config={'displayModeBar': False})
                ], className="chart-card")
            ], lg=5, xs=12)
        ]),

        # Row 2: Charts
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("Top 10 Largest Breaches", className="chart-title"),
                        html.P("Historical mega-breaches ranked by accounts compromised", className="chart-subtitle")
                    ], className="chart-header"),
                    dcc.Graph(id='chart-top-breaches', config={'displayModeBar': False})
                ], className="chart-card")
            ], lg=7, xs=12),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("Impact-Level Distribution", className="chart-title"),
                        html.P("Severity breakdown (Critical, High, Medium, Low)", className="chart-subtitle")
                    ], className="chart-header"),
                    dcc.Graph(id='chart-impact-donut', config={'displayModeBar': False})
                ], className="chart-card")
            ], lg=5, xs=12)
        ])
    ])

def render_intelligence_page(df, df_classes):
    """PAGE 2: Breach Intelligence layout."""
    return html.Div([
        # Page Title & Subtitle
        html.Div([
            html.H2("Breach Intelligence", style={'color': THEME['navy'], 'fontWeight': '800', 'marginBottom': '0.2rem'}),
            html.P("Deep Analysis of Compromised Information Types, Security Classifications, and Intelligence Latency",
                   style={'color': THEME['muted'], 'fontSize': '0.95rem', 'marginBottom': '1.25rem'})
        ]),

        # Row 1: Top exposed data classes & Security Classifications
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Top 20 Exposed Data Classes", className="chart-title"),
                            html.P("Most frequent information assets compromised across breaches", className="chart-subtitle")
                        ]),
                        dbc.RadioItems(
                            id='radio-dataclass-mode',
                            options=[
                                {'label': 'Count', 'value': 'count'},
                                {'label': 'Percentage', 'value': 'percentage'}
                            ],
                            value='count',
                            inline=True,
                            className="text-muted",
                            style={'fontSize': '0.75rem'}
                        )
                    ], className="chart-header"),
                    dcc.Graph(id='chart-data-classes', config={'displayModeBar': False})
                ], className="chart-card")
            ], lg=7, xs=12),

            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("Security Classification Analysis", className="chart-title"),
                        html.P("Comparative breakdown across 5 key security dimensions", className="chart-subtitle")
                    ], className="chart-header"),
                    dcc.Graph(id='chart-security-flags', config={'displayModeBar': False}),
                    html.Div([
                        html.Small("Dimensions: Verified vs Unverified • Sensitive vs Standard • Malware vs Non-Malware • Spam List vs Non-Spam • Fabricated vs Non-Fabricated",
                                   className="text-muted text-center d-block mt-2", style={'fontSize': '0.72rem'})
                    ])
                ], className="chart-card")
            ], lg=5, xs=12)
        ], className="mb-3"),

        # Row 2: Intelligence Latency Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("Intelligence / Disclosure Latency Analysis", className="chart-title"),
                        html.P("Elapsed time between breach occurrence (BreachDate) and public database addition (AddedDate)", className="chart-subtitle")
                    ], className="chart-header"),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='chart-latency-hist', config={'displayModeBar': False})
                        ], lg=8, xs=12),
                        dbc.Col([
                            html.Div(id='panel-latency-stats', className="p-3 border rounded bg-light", style={'height': '100%'})
                        ], lg=4, xs=12)
                    ])
                ], className="chart-card")
            ], xs=12)
        ])
    ])

def render_entity_page(df):
    """PAGE 3: Entity Analysis layout."""
    entity_options = [{'label': f"{row['Title']} ({row['Name']})", 'value': row['Name']}
                      for _, row in df.sort_values('Title').iterrows()]
    
    default_val = 'AdultFriendFinder' if 'AdultFriendFinder' in df['Name'].values else df['Name'].iloc[0]

    return html.Div([
        # Page Title & Subtitle
        html.Div([
            html.H2("Entity Intelligence", style={'color': THEME['navy'], 'fontWeight': '800', 'marginBottom': '0.2rem'}),
            html.P("Organizational Threat Profiles, Re-occurrence Patterns, and Incident Dossiers",
                   style={'color': THEME['muted'], 'fontSize': '0.95rem', 'marginBottom': '1.25rem'})
        ]),

        dbc.Row([
            # Left Column: Entity Selection & Repeated Targets
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("Entity Search & Selection", className="chart-title"),
                        html.P("Search and analyze individual breached organizations", className="chart-subtitle")
                    ], className="chart-header"),
                    html.Label("Search / Select Entity:", className="filter-label"),
                    dcc.Dropdown(
                        id='dropdown-entity-select',
                        options=entity_options,
                        value=default_val,
                        searchable=True,
                        clearable=False,
                        className="mb-3"
                    ),
                    html.Div([
                        html.Span("Quick Select: ", style={'fontSize': '0.75rem', 'fontWeight': 'bold', 'color': THEME['muted']}),
                        dbc.ButtonGroup([
                            dbc.Button("Adobe", id="btn-quick-adobe", size="sm", color="light", className="me-1 py-0 px-2", style={'fontSize': '0.75rem'}),
                            dbc.Button("LinkedIn", id="btn-quick-linkedin", size="sm", color="light", className="me-1 py-0 px-2", style={'fontSize': '0.75rem'}),
                            dbc.Button("Twitter", id="btn-quick-twitter", size="sm", color="light", className="me-1 py-0 px-2", style={'fontSize': '0.75rem'}),
                            dbc.Button("Facebook", id="btn-quick-facebook", size="sm", color="light", className="me-1 py-0 px-2", style={'fontSize': '0.75rem'}),
                            dbc.Button("Dropbox", id="btn-quick-dropbox", size="sm", color="light", className="me-1 py-0 px-2", style={'fontSize': '0.75rem'}),
                            dbc.Button("Canva", id="btn-quick-canva", size="sm", color="light", className="py-0 px-2", style={'fontSize': '0.75rem'})
                        ], size="sm", className="mb-2")
                    ])
                ], className="chart-card mb-3"),

                html.Div([
                    html.Div([
                        html.H4("Repeatedly Breached Entities", className="chart-title"),
                        html.P("Organizations suffering 2 or more distinct recorded incidents", className="chart-subtitle")
                    ], className="chart-header"),
                    dcc.Graph(id='chart-repeated-entities', config={'displayModeBar': False})
                ], className="chart-card")
            ], lg=5, xs=12),

            # Right Column: Selected Entity Dossier Panel
            dbc.Col([
                html.Div(id='panel-entity-dossier', className="chart-card")
            ], lg=7, xs=12)
        ])
    ])

def render_explorer_page(df):
    """PAGE 4: Breach Explorer interactive searchable table layout."""
    table_cols = [
        {'name': 'Name', 'id': 'Name'},
        {'name': 'Title', 'id': 'Title'},
        {'name': 'Domain', 'id': 'Domain'},
        {'name': 'Breach Date', 'id': 'BreachDate_str'},
        {'name': 'Affected Accounts', 'id': 'PwnCount', 'type': 'numeric', 'format': {'specifier': ',d'}},
        {'name': 'Impact Level', 'id': 'ImpactLevel'},
        {'name': 'Verified', 'id': 'IsVerified_str'},
        {'name': 'Sensitive', 'id': 'IsSensitive_str'},
        {'name': 'Malware', 'id': 'IsMalware_str'}
    ]

    return html.Div([
        # Page Title & Subtitle
        html.Div([
            html.H2("Breach Explorer", style={'color': THEME['navy'], 'fontWeight': '800', 'marginBottom': '0.2rem'}),
            html.P("Interactive Searchable Catalog & Granular Incident Dossier",
                   style={'color': THEME['muted'], 'fontSize': '0.95rem', 'marginBottom': '1.25rem'})
        ]),

        html.Div([
            html.Div([
                html.Div([
                    html.H4("Incident Database Catalog", className="chart-title"),
                    html.P("Search, sort, filter columns, and select a row to view full incident intelligence", className="chart-subtitle")
                ]),
                html.Div([
                    dbc.Button("⬇ Export to CSV", id="btn-export-csv", color="primary", size="sm",
                               style={'backgroundColor': THEME['violet'], 'borderColor': THEME['violet']}),
                    dcc.Download(id="download-breach-csv")
                ])
            ], className="chart-header"),

            dash_table.DataTable(
                id='table-breaches',
                columns=table_cols,
                page_size=15,
                page_action='native',
                sort_action='native',
                sort_mode='multi',
                filter_action='native',
                row_selectable='single',
                selected_rows=[0],
                style_table={'overflowX': 'auto', 'minWidth': '100%'},
                style_header={
                    'backgroundColor': '#F8FAFC',
                    'fontWeight': '700',
                    'color': THEME['navy'],
                    'borderBottom': f'2px solid {THEME["violet"]}',
                    'fontSize': '0.8rem',
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.03em'
                },
                style_cell={
                    'padding': '10px 12px',
                    'fontSize': '0.82rem',
                    'fontFamily': 'Segoe UI, sans-serif',
                    'color': THEME['navy'],
                    'borderBottom': '1px solid #F1F5F9',
                    'textAlign': 'left',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 180
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#FCFDFE'},
                    {'if': {'state': 'selected'}, 'backgroundColor': THEME['light_violet'], 'border': f'1px solid {THEME["violet"]}'},
                    {'if': {'filter_query': '{ImpactLevel} = "Critical"'}, 'color': '#DC2626', 'fontWeight': 'bold'},
                    {'if': {'filter_query': '{ImpactLevel} = "High"'}, 'color': '#EA580C', 'fontWeight': 'bold'},
                    {'if': {'filter_query': '{ImpactLevel} = "Medium"'}, 'color': '#D97706'},
                    {'if': {'filter_query': '{ImpactLevel} = "Low"'}, 'color': '#16A34A'}
                ]
            )
        ], className="chart-card mb-3"),

        html.Div(id='panel-table-dossier')
    ])
