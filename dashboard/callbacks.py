"""
callbacks.py - Reactive State Management & Interactive Callbacks
Author: Cybersecurity Analytics Team
"""

import ast
import re
import numpy as np
import pandas as pd
from dash import Input, Output, State, callback_context, html, dcc, no_update
import dash_bootstrap_components as dbc

from dashboard.config import THEME, IMPACT_COLORS, format_compact, format_full
from dashboard.charts import (
    create_breaches_over_time_chart,
    create_accounts_over_time_chart,
    create_top_breaches_chart,
    create_impact_donut_chart,
    create_latency_distribution_chart,
    create_data_classes_chart,
    create_security_classification_chart,
    create_repeated_entities_chart,
    create_entity_timeline_chart
)
from dashboard.layout import (
    render_overview_page,
    render_intelligence_page,
    render_entity_page,
    render_explorer_page
)

def register_callbacks(app, df, df_classes):
    """Register all reactive Dash callbacks."""

    # 1. Page Routing & Tab State
    @app.callback(
        [Output('page-content', 'children'),
         Output('tab-overview', 'active'),
         Output('tab-intelligence', 'active'),
         Output('tab-entity', 'active'),
         Output('tab-explorer', 'active'),
         Output('store-active-page', 'data')],
        [Input('tab-overview', 'n_clicks'),
         Input('tab-intelligence', 'n_clicks'),
         Input('tab-entity', 'n_clicks'),
         Input('tab-explorer', 'n_clicks')],
        [State('store-active-page', 'data')]
    )
    def switch_page(n_ov, n_intel, n_ent, n_exp, current_page):
        ctx = callback_context
        if not ctx.triggered:
            page = current_page or 'overview'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'tab-overview':
                page = 'overview'
            elif button_id == 'tab-intelligence':
                page = 'intelligence'
            elif button_id == 'tab-entity':
                page = 'entity'
            elif button_id == 'tab-explorer':
                page = 'explorer'
            else:
                page = 'overview'

        is_ov = (page == 'overview')
        is_intel = (page == 'intelligence')
        is_ent = (page == 'entity')
        is_exp = (page == 'explorer')

        if page == 'overview':
            content = render_overview_page(df)
        elif page == 'intelligence':
            content = render_intelligence_page(df, df_classes)
        elif page == 'entity':
            content = render_entity_page(df)
        elif page == 'explorer':
            content = render_explorer_page(df)
        else:
            content = render_overview_page(df)

        return content, is_ov, is_intel, is_ent, is_exp, page

    # 2. Reset Filters
    @app.callback(
        [Output('filter-year-range', 'value'),
         Output('filter-impact-level', 'value'),
         Output('filter-verification', 'value'),
         Output('filter-sensitivity', 'value')],
        [Input('btn-reset-filters', 'n_clicks')]
    )
    def reset_filters(n_clicks):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        min_year = int(df['BreachYear'].min())
        max_year = int(df['BreachYear'].max())
        return [min_year, max_year], ['Critical', 'High', 'Medium', 'Low'], 'ALL', 'ALL'

    # 3. Global Filter Pipeline Store
    @app.callback(
        Output('store-filtered-indices', 'data'),
        [Input('filter-year-range', 'value'),
         Input('filter-impact-level', 'value'),
         Input('filter-verification', 'value'),
         Input('filter-sensitivity', 'value')]
    )
    def filter_dataset(year_range, impact_levels, verification, sensitivity):
        mask = pd.Series(True, index=df.index)

        # Year filter
        if year_range and len(year_range) == 2:
            mask &= (df['BreachYear'] >= year_range[0]) & (df['BreachYear'] <= year_range[1])

        # Impact level filter
        if impact_levels:
            mask &= df['ImpactLevel'].isin(impact_levels)

        # Verification filter
        if verification == 'VERIFIED':
            mask &= (df['IsVerified'] == True)
        elif verification == 'UNVERIFIED':
            mask &= (df['IsVerified'] == False)

        # Sensitivity filter
        if sensitivity == 'SENSITIVE':
            mask &= (df['IsSensitive'] == True)
        elif sensitivity == 'STANDARD':
            mask &= (df['IsSensitive'] == False)

        filtered_idx = df[mask].index.tolist()
        return filtered_idx

    # 4. Page 1: Overview KPIs & Charts
    @app.callback(
        [Output('kpi-val-total-breaches', 'children'),
         Output('kpi-sub-total-breaches', 'children'),
         Output('kpi-val-total-accounts', 'children'),
         Output('kpi-sub-total-accounts', 'children'),
         Output('kpi-val-avg-size', 'children'),
         Output('kpi-sub-avg-size', 'children'),
         Output('kpi-val-max-breach', 'children'),
         Output('kpi-sub-max-breach', 'children'),
         Output('kpi-val-verified-breaches', 'children'),
         Output('kpi-sub-verified-breaches', 'children'),
         Output('kpi-val-sensitive-breaches', 'children'),
         Output('kpi-sub-sensitive-breaches', 'children'),
         Output('kpi-val-malware-breaches', 'children'),
         Output('kpi-sub-malware-breaches', 'children'),
         Output('kpi-val-critical-breaches', 'children'),
         Output('kpi-sub-critical-breaches', 'children'),
         Output('chart-breaches-over-time', 'figure'),
         Output('chart-accounts-over-time', 'figure'),
         Output('chart-top-breaches', 'figure'),
         Output('chart-impact-donut', 'figure')],
        [Input('store-filtered-indices', 'data'),
         Input('radio-account-scale', 'value'),
         Input('store-active-page', 'data')]
    )
    def update_overview(indices, account_scale, active_page):
        if active_page != 'overview':
            return [no_update] * 20

        sub_df = df.loc[indices] if indices else df.iloc[0:0]

        total_b = len(sub_df)
        total_acc = int(sub_df['PwnCount'].sum()) if total_b > 0 else 0
        avg_acc = float(sub_df['PwnCount'].mean()) if total_b > 0 else 0
        max_acc = int(sub_df['PwnCount'].max()) if total_b > 0 else 0
        max_record = sub_df.loc[sub_df['PwnCount'].idxmax()]['Title'] if total_b > 0 else "N/A"

        ver_count = int(sub_df['IsVerified'].sum()) if total_b > 0 else 0
        sens_count = int(sub_df['IsSensitive'].sum()) if total_b > 0 else 0
        mal_count = int(sub_df['IsMalware'].sum()) if total_b > 0 else 0
        crit_count = int(sub_df['ImpactLevel'].isin(['Critical', 'High']).sum()) if total_b > 0 else 0

        pct_ver = (ver_count / total_b * 100) if total_b > 0 else 0
        pct_sens = (sens_count / total_b * 100) if total_b > 0 else 0
        pct_crit = (crit_count / total_b * 100) if total_b > 0 else 0

        is_log = (account_scale == 'log')

        fig_time = create_breaches_over_time_chart(sub_df)
        fig_acc = create_accounts_over_time_chart(sub_df, is_log=is_log)
        fig_top = create_top_breaches_chart(sub_df, top_n=10)
        fig_donut = create_impact_donut_chart(sub_df)

        return (
            f"{total_b:,}", f"{(total_b / len(df) * 100):.1f}% of global corpus",
            format_compact(total_acc), f"{total_acc:,} total exposed",
            format_compact(avg_acc), f"Median: {format_compact(sub_df['PwnCount'].median()) if total_b > 0 else '0'}",
            format_compact(max_acc), f"{max_record[:20]}...",
            f"{ver_count:,}", f"{pct_ver:.1f}% verified rate",
            f"{sens_count:,}", f"{pct_sens:.1f}% sensitive rate",
            f"{mal_count:,}", f"Malware stealer dumps",
            f"{crit_count:,}", f"{pct_crit:.1f}% severity (≥1M)",
            fig_time, fig_acc, fig_top, fig_donut
        )

    # 5. Page 2: Breach Intelligence Callbacks
    @app.callback(
        [Output('chart-data-classes', 'figure'),
         Output('chart-security-flags', 'figure'),
         Output('chart-latency-hist', 'figure'),
         Output('panel-latency-stats', 'children')],
        [Input('store-filtered-indices', 'data'),
         Input('radio-dataclass-mode', 'value'),
         Input('store-active-page', 'data')]
    )
    def update_intelligence(indices, dataclass_mode, active_page):
        if active_page != 'intelligence':
            return no_update, no_update, no_update, no_update

        sub_df = df.loc[indices] if indices else df.iloc[0:0]
        sub_names = set(sub_df['Name'])
        sub_classes = df_classes[df_classes['BreachName'].isin(sub_names)]

        mode = dataclass_mode or 'count'
        fig_classes = create_data_classes_chart(sub_classes, len(sub_df), top_n=20, mode=mode)
        fig_flags = create_security_classification_chart(sub_df)
        fig_latency = create_latency_distribution_chart(sub_df)

        # Intelligence Latency Summary Box
        latency_series = sub_df['DaysToDatabaseAddition']
        if not latency_series.empty:
            mean_lat = latency_series.mean()
            med_lat = latency_series.median()
            p25 = np.percentile(latency_series, 25)
            p75 = np.percentile(latency_series, 75)
            p90 = np.percentile(latency_series, 90)
            p95 = np.percentile(latency_series, 95)
            max_lat = latency_series.max()

            latency_stats_panel = html.Div([
                html.H6("Latency Statistical Summary", style={'color': THEME['navy'], 'fontWeight': '800'}),
                html.P("Intelligence latency measures the elapsed time from incident occurrence (BreachDate) to ingestion in the public intelligence database (AddedDate).",
                       style={'fontSize': '0.75rem', 'color': THEME['muted'], 'marginBottom': '0.75rem'}),
                html.Table([
                    html.Tr([html.Td(html.Strong("Median Latency:"), style={'padding': '4px 8px'}),
                             html.Td(f"{med_lat:.0f} days (~{med_lat/30.4:.1f} months)", style={'padding': '4px 8px', 'color': THEME['violet'], 'fontWeight': 'bold'})]),
                    html.Tr([html.Td(html.Strong("Average (Mean) Latency:"), style={'padding': '4px 8px'}),
                             html.Td(f"{mean_lat:.1f} days (~{mean_lat/365.25:.1f} years)", style={'padding': '4px 8px'})]),
                    html.Tr([html.Td("25th Percentile (Q1):", style={'padding': '4px 8px'}),
                             html.Td(f"{p25:.0f} days", style={'padding': '4px 8px'})]),
                    html.Tr([html.Td("75th Percentile (Q3):", style={'padding': '4px 8px'}),
                             html.Td(f"{p75:.0f} days", style={'padding': '4px 8px'})]),
                    html.Tr([html.Td("90th Percentile:", style={'padding': '4px 8px'}),
                             html.Td(f"{p90:.0f} days", style={'padding': '4px 8px'})]),
                    html.Tr([html.Td("95th Percentile:", style={'padding': '4px 8px'}),
                             html.Td(f"{p95:.0f} days", style={'padding': '4px 8px'})]),
                    html.Tr([html.Td("Maximum Observed Latency:", style={'padding': '4px 8px'}),
                             html.Td(f"{max_lat:,} days (~{max_lat/365.25:.1f} years)", style={'padding': '4px 8px', 'color': '#DC2626'})]),
                ], style={'width': '100%', 'fontSize': '0.8rem', 'backgroundColor': '#FFFFFF', 'borderRadius': '6px', 'border': '1px solid #E2E8F0'}),
                html.Div([
                    html.Small("Insight: 25% of breaches remained publicly undetected or undisclosed for over 2 years, posing severe credential-stuffing vulnerability windows.",
                               className="text-muted d-block mt-2", style={'fontSize': '0.72rem', 'fontStyle': 'italic'})
                ])
            ])
        else:
            latency_stats_panel = html.Div("No latency data available for current selection.", className="text-muted")

        return fig_classes, fig_flags, fig_latency, latency_stats_panel

    # 6. Page 3: Entity Analysis
    @app.callback(
        Output('dropdown-entity-select', 'value'),
        [Input('btn-quick-adobe', 'n_clicks'),
         Input('btn-quick-linkedin', 'n_clicks'),
         Input('btn-quick-twitter', 'n_clicks'),
         Input('btn-quick-facebook', 'n_clicks'),
         Input('btn-quick-dropbox', 'n_clicks'),
         Input('btn-quick-canva', 'n_clicks')]
    )
    def quick_entity_select(c1, c2, c3, c4, c5, c6):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        btn = ctx.triggered[0]['prop_id'].split('.')[0]
        mapping = {
            'btn-quick-adobe': 'Adobe',
            'btn-quick-linkedin': 'LinkedIn',
            'btn-quick-twitter': 'Twitter',
            'btn-quick-facebook': 'Facebook',
            'btn-quick-dropbox': 'Dropbox',
            'btn-quick-canva': 'Canva'
        }
        return mapping.get(btn, no_update)

    @app.callback(
        [Output('chart-repeated-entities', 'figure'),
         Output('panel-entity-dossier', 'children')],
        [Input('dropdown-entity-select', 'value'),
         Input('store-active-page', 'data')]
    )
    def update_entity_view(selected_entity, active_page):
        if active_page != 'entity':
            return no_update, no_update

        fig_repeats = create_repeated_entities_chart(df, top_n=10)

        if not selected_entity or selected_entity not in df['Name'].values:
            selected_entity = df['Name'].iloc[0]

        record = df[df['Name'] == selected_entity].iloc[0]
        domain = record['Domain']
        
        # Find all recorded breaches for this entity / domain
        if domain != 'N/A (No Domain / Aggregated Corpus)':
            entity_breaches = df[df['Domain'] == domain].copy()
        else:
            entity_breaches = df[df['Name'] == selected_entity].copy()

        total_breaches_for_entity = len(entity_breaches)
        total_accounts_entity = int(entity_breaches['PwnCount'].sum())
        max_breach_entity = int(entity_breaches['PwnCount'].max())
        avg_breach_entity = float(entity_breaches['PwnCount'].mean())

        # Security Status Badges
        impact_cls = f"badge-{record['ImpactLevel'].lower()}"
        ver_badge = html.Span("Verified" if record['IsVerified'] else "Unverified",
                              className="badge-verified" if record['IsVerified'] else "badge-unverified",
                              style={'marginRight': '0.4rem'})
        sens_badge = html.Span("Sensitive" if record['IsSensitive'] else "Standard Privacy",
                               className="badge-sensitive" if record['IsSensitive'] else "badge-unverified",
                               style={'marginRight': '0.4rem'})
        mal_badge = html.Span("Malware-Associated" if record['IsMalware'] else "Non-Malware",
                              className="badge-malware" if record['IsMalware'] else "badge-unverified",
                              style={'marginRight': '0.4rem'})

        badges = [
            html.Span(f"{record['ImpactLevel']} Impact", className=impact_cls, style={'marginRight': '0.4rem'}),
            ver_badge,
            sens_badge,
            mal_badge
        ]
        if record['IsFabricated']:
            badges.append(html.Span("Fabricated Claim", className="badge-high", style={'marginRight': '0.4rem'}))

        # Parse data classes
        raw_classes = record['DataClasses']
        try:
            parsed_classes = ast.literal_eval(raw_classes) if isinstance(raw_classes, str) else []
        except Exception:
            parsed_classes = []

        class_tags = [html.Span(cls, className="data-class-tag") for cls in parsed_classes]
        clean_desc = re.sub(r'<[^>]+>', '', record['Description'])

        # Timeline
        timeline_fig = create_entity_timeline_chart(entity_breaches)

        dossier = html.Div([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H3(record['Title'], style={'color': THEME['navy'], 'fontWeight': '800', 'margin': 0}),
                        html.Div([
                            html.A(record['Domain'], href=f"https://{record['Domain']}" if not record['Domain'].startswith('N/A') else "#",
                                   target="_blank", style={'color': THEME['blue'], 'fontSize': '0.85rem', 'textDecoration': 'none', 'fontWeight': '600'}),
                            html.Span(f" • Identifier: {record['Name']}", style={'color': THEME['muted'], 'fontSize': '0.8rem', 'marginLeft': '0.5rem'})
                        ])
                    ], md=7, xs=12),
                    dbc.Col([
                        html.Div(badges, className="d-flex flex-wrap justify-content-md-end mt-2 mt-md-0")
                    ], md=5, xs=12)
                ])
            ], className="dossier-header"),

            # Entity Metric Indicators
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Recorded Breaches", className="kpi-title"),
                        html.Div(f"{total_breaches_for_entity}", className="kpi-value", style={'fontSize': '1.35rem', 'color': THEME['violet']}),
                        html.Div("Targeted incidents", className="kpi-subtext")
                    ], className="p-2 border rounded bg-white text-center")
                ], xs=4),
                dbc.Col([
                    html.Div([
                        html.Div("Total Affected", className="kpi-title"),
                        html.Div(format_compact(total_accounts_entity), className="kpi-value", style={'fontSize': '1.35rem', 'color': THEME['blue']}),
                        html.Div(f"{total_accounts_entity:,} accounts", className="kpi-subtext")
                    ], className="p-2 border rounded bg-white text-center")
                ], xs=4),
                dbc.Col([
                    html.Div([
                        html.Div("Largest Breach", className="kpi-title"),
                        html.Div(format_compact(max_breach_entity), className="kpi-value", style={'fontSize': '1.35rem', 'color': THEME['teal']}),
                        html.Div("Peak footprint", className="kpi-subtext")
                    ], className="p-2 border rounded bg-white text-center")
                ], xs=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Average Breach Size", className="kpi-title"),
                        html.Div(format_compact(avg_breach_entity), className="kpi-value", style={'fontSize': '1.2rem', 'color': THEME['navy']}),
                        html.Div(f"{avg_breach_entity:,.0f} accounts", className="kpi-subtext")
                    ], className="p-2 border rounded bg-white text-center")
                ], xs=4),
                dbc.Col([
                    html.Div([
                        html.Div("Verification", className="kpi-title"),
                        html.Div("Verified" if record['IsVerified'] else "Unverified",
                                 className="kpi-value", style={'fontSize': '1.15rem', 'color': THEME['teal'] if record['IsVerified'] else THEME['muted']}),
                        html.Div("Subscriber cross-check", className="kpi-subtext")
                    ], className="p-2 border rounded bg-white text-center")
                ], xs=4),
                dbc.Col([
                    html.Div([
                        html.Div("Incident Age", className="kpi-title"),
                        html.Div(f"{record['BreachAgeYears']} Years", className="kpi-value", style={'fontSize': '1.2rem', 'color': THEME['navy']}),
                        html.Div(f"Occurred {record['BreachDate'].strftime('%Y-%m-%d')}", className="kpi-subtext")
                    ], className="p-2 border rounded bg-white text-center")
                ], xs=4),
            ], className="mb-3"),

            # Breach Timeline Chart
            html.Div([
                html.Label("Breach Timeline (Historical Incidents):", className="filter-label"),
                dcc.Graph(figure=timeline_fig, config={'displayModeBar': False})
            ], className="mb-3"),

            # Exposed Data Classes
            html.Div([
                html.Label(f"Exposed Information Assets ({len(parsed_classes)} classes):", className="filter-label"),
                html.Div(class_tags, className="d-flex flex-wrap p-2 border rounded bg-light mb-3")
            ]),

            # Detailed Incident Narrative
            html.Div([
                html.Label("Breach Intelligence Narrative:", className="filter-label"),
                html.Div(clean_desc, style={'fontSize': '0.85rem', 'lineHeight': '1.5', 'color': THEME['navy'], 'padding': '0.75rem', 'backgroundColor': '#FFFFFF', 'borderRadius': '6px', 'border': '1px solid #E2E8F0'})
            ])
        ])

        return fig_repeats, dossier

    # 7. Page 4: Breach Explorer DataTable & Detail Panel
    @app.callback(
        [Output('table-breaches', 'data'),
         Output('panel-table-dossier', 'children')],
        [Input('store-filtered-indices', 'data'),
         Input('table-breaches', 'selected_rows'),
         Input('store-active-page', 'data')]
    )
    def update_explorer(indices, selected_rows, active_page):
        if active_page != 'explorer':
            return no_update, no_update

        sub_df = df.loc[indices].copy() if indices else df.iloc[0:0].copy()
        
        # Prepare display string formats
        sub_df['BreachDate_str'] = sub_df['BreachDate'].dt.strftime('%Y-%m-%d')
        sub_df['IsVerified_str'] = sub_df['IsVerified'].map({True: 'Verified', False: 'Unverified'})
        sub_df['IsSensitive_str'] = sub_df['IsSensitive'].map({True: 'Sensitive', False: 'Standard'})
        sub_df['IsMalware_str'] = sub_df['IsMalware'].map({True: 'Malware', False: 'Standard'})

        table_data = sub_df.to_dict('records')

        if not selected_rows or selected_rows[0] >= len(table_data):
            selected_idx = 0 if len(table_data) > 0 else None
        else:
            selected_idx = selected_rows[0]

        if selected_idx is not None and len(table_data) > 0:
            sel_row = table_data[selected_idx]
            
            raw_classes = sel_row.get('DataClasses', '[]')
            try:
                classes = ast.literal_eval(raw_classes) if isinstance(raw_classes, str) else []
            except Exception:
                classes = []

            tags = [html.Span(c, className="data-class-tag") for c in classes]
            clean_desc = re.sub(r'<[^>]+>', '', sel_row.get('Description', ''))

            dossier = html.Div([
                html.Div([
                    html.H5(f"Selected Incident Intelligence: {sel_row.get('Title')} ({sel_row.get('Name')})",
                            style={'color': THEME['navy'], 'fontWeight': '800', 'margin': 0}),
                    html.Span(f"Domain: {sel_row.get('Domain')} • Breach Date: {sel_row.get('BreachDate_str')} • Affected Accounts: {format_full(sel_row.get('PwnCount'))}",
                              style={'color': THEME['muted'], 'fontSize': '0.8rem'})
                ], className="chart-header"),

                dbc.Row([
                    dbc.Col([
                        html.Label("Security Flags & Impact:", className="filter-label"),
                        html.Div([
                            html.Span(f"{sel_row.get('ImpactLevel')} Impact", className=f"badge-{sel_row.get('ImpactLevel', 'low').lower()}", style={'marginRight': '0.4rem'}),
                            html.Span(sel_row.get('IsVerified_str'), className="badge-verified" if sel_row.get('IsVerified') else "badge-unverified", style={'marginRight': '0.4rem'}),
                            html.Span(sel_row.get('IsSensitive_str'), className="badge-sensitive" if sel_row.get('IsSensitive') else "badge-unverified", style={'marginRight': '0.4rem'}),
                            html.Span(sel_row.get('IsMalware_str'), className="badge-malware" if sel_row.get('IsMalware') else "badge-unverified")
                        ], className="d-flex flex-wrap mb-2")
                    ], md=6, xs=12),
                    dbc.Col([
                        html.Label(f"Exposed Information Assets ({len(classes)}):", className="filter-label"),
                        html.Div(tags, className="d-flex flex-wrap mb-2")
                    ], md=6, xs=12)
                ]),

                html.Div([
                    html.Label("Detailed Incident Narrative:", className="filter-label"),
                    html.Div(clean_desc, style={'fontSize': '0.83rem', 'color': THEME['navy'], 'lineHeight': '1.5', 'padding': '0.75rem', 'backgroundColor': '#F8FAFC', 'borderRadius': '6px', 'border': '1px solid #E2E8F0'})
                ])
            ], className="chart-card")
        else:
            dossier = html.Div("Select an incident row above to inspect the complete dossier.", className="text-muted p-3")

        return table_data, dossier

    # 8. Export CSV Download Callback
    @app.callback(
        Output("download-breach-csv", "data"),
        Input("btn-export-csv", "n_clicks"),
        [State('store-filtered-indices', 'data')],
        prevent_initial_call=True
    )
    def export_csv(n_clicks, indices):
        if not n_clicks:
            return no_update
        export_df = df.loc[indices] if indices else df
        cols_to_export = ['Name', 'Title', 'Domain', 'BreachDate', 'AddedDate', 'ModifiedDate',
                          'PwnCount', 'ImpactLevel', 'IsVerified', 'IsSensitive', 'IsMalware',
                          'IsSpamList', 'IsFabricated', 'DaysToDatabaseAddition', 'DataClasses']
        subset_export = export_df[[c for c in cols_to_export if c in export_df.columns]]
        return dcc.send_data_frame(subset_export.to_csv, "cybersecurity_breaches_export.csv", index=False)
