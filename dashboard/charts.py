"""
charts.py - Plotly Visualizations Engine for Cybersecurity Intelligence Platform
Author: Cybersecurity Analytics Team
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dashboard.config import THEME, IMPACT_COLORS, PLOTLY_TEMPLATE, format_compact, format_full

def apply_clean_layout(fig, title="", height=360):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        title={
            'text': f"<b>{title}</b>" if title else "",
            'font': {'size': 13, 'color': THEME['navy'], 'family': 'Segoe UI'},
            'x': 0.02,
            'y': 0.95
        },
        margin=dict(l=35, r=25, t=45 if title else 25, b=35),
        hoverlabel=dict(
            bgcolor=THEME['navy'],
            font_size=12,
            font_family="Segoe UI",
            font_color="#FFFFFF"
        )
    )
    return fig

def create_breaches_over_time_chart(df):
    """Annual breach frequency with cumulative incident progression."""
    if df.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No data available for current filters")

    yearly = df.groupby('BreachYear').size().reset_index(name='Count')
    yearly = yearly.sort_values('BreachYear')
    yearly['Cumulative'] = yearly['Count'].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=yearly['BreachYear'],
        y=yearly['Count'],
        name='Annual Breaches',
        mode='lines+markers',
        line=dict(color=THEME['violet'], width=3),
        marker=dict(size=7, color=THEME['violet'], symbol='circle'),
        fill='tozeroy',
        fillcolor='rgba(109, 40, 217, 0.08)',
        hovertemplate="<b>Year %{x}</b><br>Incidents: %{y:,}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=yearly['BreachYear'],
        y=yearly['Cumulative'],
        name='Cumulative Incidents',
        mode='lines',
        line=dict(color=THEME['blue'], width=2, dash='dot'),
        yaxis='y2',
        hovertemplate="<b>Cumulative Total</b>: %{y:,}<extra></extra>"
    ))

    fig.update_layout(
        yaxis=dict(title='Annual Breaches', linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        yaxis2=dict(
            title='Cumulative Breaches',
            overlaying='y',
            side='right',
            showgrid=False,
            linecolor=THEME['border'],
            tickfont=dict(color=THEME['blue'], size=10)
        ),
        xaxis=dict(
            title='Breach Year',
            tickmode='linear',
            dtick=1 if len(yearly) <= 12 else 2,
            linecolor=THEME['border'],
            gridcolor=THEME['border_subtle']
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return apply_clean_layout(fig, "Annual Breach Frequency & Cumulative Progression", height=340)

def create_accounts_over_time_chart(df, is_log=False):
    """Accounts affected by year with toggle between linear and log scale."""
    if df.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No data available for current filters")

    yearly = df.groupby('BreachYear')['PwnCount'].sum().reset_index()
    yearly = yearly.sort_values('BreachYear')

    y_vals = np.log10(yearly['PwnCount'].replace(0, 1)) if is_log else yearly['PwnCount'] / 1e6
    y_title = "Log10(Compromised Accounts)" if is_log else "Accounts Compromised (Millions)"

    fig = go.Figure(go.Bar(
        x=yearly['BreachYear'],
        y=y_vals,
        marker=dict(
            color=THEME['blue'],
            line=dict(color=THEME['navy'], width=0.5)
        ),
        customdata=yearly['PwnCount'],
        hovertemplate="<b>Year %{x}</b><br>Total Affected: %{customdata:,} accounts<extra></extra>"
    ))

    fig.update_layout(
        xaxis=dict(title='Breach Year', tickmode='linear', dtick=1 if len(yearly) <= 12 else 2, linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        yaxis=dict(title=y_title, linecolor=THEME['border'], gridcolor=THEME['border_subtle'])
    )

    return apply_clean_layout(fig, f"Accounts Affected by Year ({'Log10 Scale' if is_log else 'Linear Millions'})", height=340)

def create_top_breaches_chart(df, top_n=10):
    """Top 10 largest breaches."""
    if df.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No data available for current filters")

    top_df = df.nlargest(top_n, 'PwnCount').sort_values('PwnCount', ascending=True)
    colors = [IMPACT_COLORS.get(imp, THEME['violet']) for imp in top_df['ImpactLevel']]

    fig = go.Figure(go.Bar(
        x=top_df['PwnCount'] / 1e6,
        y=top_df['Title'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x),
        orientation='h',
        marker=dict(color=colors, line=dict(color=THEME['navy'], width=0.5)),
        text=[f" {format_compact(val)}" for val in top_df['PwnCount']],
        textposition='outside',
        customdata=list(zip(top_df['Name'], top_df['PwnCount'], top_df['ImpactLevel'], top_df['BreachYear'])),
        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[3]})<br>Severity: %{customdata[2]}<br>Accounts: %{customdata[1]:,}<extra></extra>"
    ))

    fig.update_layout(
        xaxis=dict(title='Compromised Accounts (Millions)', linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        yaxis=dict(linecolor=THEME['border'], gridcolor=THEME['border_subtle'])
    )

    return apply_clean_layout(fig, f"Top {top_n} Largest Data Breaches", height=360)

def create_impact_donut_chart(df):
    """Impact-level distribution donut chart."""
    if df.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No data available for current filters")

    counts = df['ImpactLevel'].value_counts()
    order = ['Critical', 'High', 'Medium', 'Low']
    labels = [k for k in order if k in counts]
    values = [counts[k] for k in labels]
    colors = [IMPACT_COLORS[k] for k in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.58,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
        textinfo='percent+label',
        textposition='outside',
        direction='clockwise',
        sort=False,
        hovertemplate="<b>%{label} Severity</b><br>Breaches: %{value:,} (%{percent})<extra></extra>"
    ))

    fig.update_layout(
        showlegend=False,
        annotations=[dict(text=f"<b>{len(df):,}</b><br><span style='font-size:10px; color:#64748B;'>Breaches</span>",
                          x=0.5, y=0.5, font_size=15, font_family="Segoe UI", showarrow=False)]
    )

    return apply_clean_layout(fig, "Impact-Level Severity Distribution", height=340)

def create_latency_distribution_chart(df):
    """Distribution of intelligence latency (DaysToDatabaseAddition)."""
    if df.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No data available for current filters")

    clipped_days = df['DaysToDatabaseAddition'].clip(upper=1500)
    fig = go.Figure(go.Histogram(
        x=clipped_days,
        nbinsx=32,
        marker=dict(color=THEME['violet'], line=dict(color='#FFFFFF', width=1)),
        hovertemplate="Latency: %{x} days<br>Breaches: %{y:,}<extra></extra>"
    ))

    med = df['DaysToDatabaseAddition'].median()
    mean_val = df['DaysToDatabaseAddition'].mean()
    fig.add_vline(x=med, line_dash="dash", line_color="#DC2626", line_width=2,
                  annotation_text=f"Median: {med:.0f}d", annotation_position="top right")

    fig.update_layout(
        xaxis=dict(title='Days Elapsed (Capped at 1,500d)', linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        yaxis=dict(title='Breach Count', linecolor=THEME['border'], gridcolor=THEME['border_subtle'])
    )

    return apply_clean_layout(fig, "Intelligence Latency Distribution", height=340)

def create_data_classes_chart(df_classes, total_breaches, top_n=20, mode='count'):
    """Top 20 exposed data classes with count/percentage toggle."""
    if df_classes.empty or total_breaches == 0:
        fig = go.Figure()
        return apply_clean_layout(fig, "No DataClass records found")

    top_c = df_classes['DataClass'].value_counts().head(top_n).sort_values(ascending=True)

    if mode == 'percentage':
        x_vals = (top_c.values / total_breaches) * 100
        x_title = "Percentage of Total Breaches (%)"
        text_labels = [f" {v:.1f}%" for v in x_vals]
        h_template = "<b>%{y}</b><br>Compromised in %{x:.1f}% of breaches<extra></extra>"
    else:
        x_vals = top_c.values
        x_title = "Breach Incident Count"
        text_labels = [f" {v:,}" for v in x_vals]
        h_template = "<b>%{y}</b><br>Compromised in: %{x:,} breaches<extra></extra>"

    fig = go.Figure(go.Bar(
        x=x_vals,
        y=top_c.index,
        orientation='h',
        marker=dict(
            color=THEME['violet'],
            line=dict(color=THEME['navy'], width=0.5)
        ),
        text=text_labels,
        textposition='outside',
        hovertemplate=h_template
    ))

    fig.update_layout(
        xaxis=dict(title=x_title, linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        yaxis=dict(linecolor=THEME['border'], gridcolor=THEME['border_subtle'])
    )

    return apply_clean_layout(fig, f"Top {top_n} Most Frequently Exposed Data Classes ({mode.title()})", height=500)

def create_security_classification_chart(df):
    """Categorical breakdown of binary security classifications."""
    if df.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No data available")

    categories = [
        ('Verification', 'Verified', df['IsVerified'].sum(), 'Unverified', (~df['IsVerified']).sum()),
        ('Sensitivity', 'Sensitive', df['IsSensitive'].sum(), 'Standard', (~df['IsSensitive']).sum()),
        ('Malware', 'Malware', df['IsMalware'].sum(), 'Non-Malware', (~df['IsMalware']).sum()),
        ('Spam List', 'Spam List', df['IsSpamList'].sum(), 'Non-Spam', (~df['IsSpamList']).sum()),
        ('Fabricated', 'Fabricated', df['IsFabricated'].sum(), 'Non-Fabricated', (~df['IsFabricated']).sum()),
    ]

    cat_names = [c[0] for c in categories]
    flag_counts = [c[2] for c in categories]
    non_flag_counts = [c[4] for c in categories]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Flagged Status',
        x=cat_names,
        y=flag_counts,
        marker=dict(color=THEME['violet']),
        text=[f"{v:,}" for v in flag_counts],
        textposition='outside',
        hovertemplate="<b>%{x} (Flagged)</b>: %{y:,} breaches<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        name='Standard / Baseline',
        x=cat_names,
        y=non_flag_counts,
        marker=dict(color=THEME['light_violet'], line=dict(color=THEME['violet'], width=1)),
        text=[f"{v:,}" for v in non_flag_counts],
        textposition='outside',
        hovertemplate="<b>%{x} (Standard)</b>: %{y:,} breaches<extra></extra>"
    ))

    fig.update_layout(
        barmode='group',
        yaxis=dict(title='Breach Count', linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        xaxis=dict(linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return apply_clean_layout(fig, "Security Classification Dimension Breakdown", height=360)

def create_repeated_entities_chart(df, top_n=10):
    """Ranking repeated entity breaches."""
    valid_domains = df[df['Domain'] != 'N/A (No Domain / Aggregated Corpus)']
    counts = valid_domains['Domain'].value_counts()
    repeats = counts[counts > 1].head(top_n).sort_values(ascending=True)

    if repeats.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No repeated entities found")

    fig = go.Figure(go.Bar(
        x=repeats.values,
        y=repeats.index,
        orientation='h',
        marker=dict(color=THEME['blue'], line=dict(color=THEME['navy'], width=0.5)),
        text=[f" {v} breaches" for v in repeats.values],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Recorded Incidents: %{x}<extra></extra>"
    ))

    fig.update_layout(
        xaxis=dict(title='Recorded Breach Count', dtick=1, linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        yaxis=dict(linecolor=THEME['border'], gridcolor=THEME['border_subtle'])
    )

    return apply_clean_layout(fig, f"Top {top_n} Entities with Multiple Recorded Breaches", height=360)

def create_entity_timeline_chart(entity_df):
    """Timeline scatter plot of incident history for a selected entity."""
    if entity_df.empty:
        fig = go.Figure()
        return apply_clean_layout(fig, "No incident history found for this entity")

    sorted_df = entity_df.sort_values('BreachDate')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sorted_df['BreachDate'],
        y=[1] * len(sorted_df),
        mode='lines+markers',
        line=dict(color=THEME['violet'], width=2),
        marker=dict(
            size=[max(14, min(35, np.log10(p + 1) * 4)) for p in sorted_df['PwnCount']],
            color=[IMPACT_COLORS.get(imp, THEME['violet']) for imp in sorted_df['ImpactLevel']],
            line=dict(color=THEME['navy'], width=1.5)
        ),
        text=sorted_df['Title'],
        customdata=list(zip(sorted_df['PwnCount'], sorted_df['ImpactLevel'], sorted_df['BreachDate'].dt.strftime('%Y-%m-%d'))),
        hovertemplate="<b>%{text}</b><br>Date: %{customdata[2]}<br>Severity: %{customdata[1]}<br>Affected: %{customdata[0]:,} accounts<extra></extra>"
    ))

    fig.update_layout(
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(title='Breach Date', linecolor=THEME['border'], gridcolor=THEME['border_subtle']),
        showlegend=False
    )

    return apply_clean_layout(fig, "Breach Timeline: Historical Incidents", height=180)
