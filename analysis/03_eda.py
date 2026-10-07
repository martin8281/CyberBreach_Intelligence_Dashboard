"""
03_eda.py - Exploratory Data Analysis & Publication-Grade Visualizations
Author: Cybersecurity Analytics Team
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

COLOR_VIOLET = '#6D28D9'
COLOR_BLUE = '#1D4ED8'
COLOR_NAVY = '#0F172A'
COLOR_LIGHT_VIOLET = '#EDE9FE'
COLOR_BORDER = '#E2E8F0'
PALETTE_IMPACT = {
    'Critical': '#DC2626',
    'High': '#EA580C',
    'Medium': '#D97706',
    'Low': '#16A34A'
}

def setup_style():
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['axes.edgecolor'] = COLOR_BORDER
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#F1F5F9'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7

def generate_eda_figures():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_path = os.path.join(base_dir, 'data', 'cleaned_breach_data.csv')
    classes_path = os.path.join(base_dir, 'data', 'breach_data_classes.csv')
    fig_dir = os.path.join(base_dir, 'outputs', 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    setup_style()
    df = pd.read_csv(cleaned_path)
    df_classes = pd.read_csv(classes_path)

    print(f"[*] Generating EDA figures from {len(df)} records into: {fig_dir}")

    # 1. pwncount_distribution.png (Raw PwnCount distribution)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.hist(df['PwnCount'] / 1e6, bins=45, color=COLOR_BLUE, edgecolor='white', alpha=0.85)
    ax.set_title("Distribution of Raw Breach Size (Millions of Compromised Accounts)", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Affected Accounts (Millions)", fontsize=11, color=COLOR_NAVY)
    ax.set_ylabel("Breach Incident Count", fontsize=11, color=COLOR_NAVY)
    ax.axvline(df['PwnCount'].median() / 1e6, color=COLOR_VIOLET, linestyle='--', linewidth=2, label=f"Median: {df['PwnCount'].median()/1e6:.2f}M")
    ax.axvline(df['PwnCount'].mean() / 1e6, color='#DC2626', linestyle=':', linewidth=2, label=f"Mean: {df['PwnCount'].mean()/1e6:.2f}M")
    ax.legend(frameon=True, facecolor='white')
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'pwncount_distribution.png'))
    plt.close()
    print("  [+] Saved pwncount_distribution.png")

    # 2. pwncount_log_distribution.png (Log-transformed distribution)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    log_pwn = np.log10(df['PwnCount'].replace(0, 1))
    sns.histplot(log_pwn, kde=True, ax=ax, color=COLOR_VIOLET, edgecolor='white', bins=35)
    ax.set_title("Log10-Transformed Distribution of Affected Accounts (Skewness Mitigation)", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Log10(PwnCount)", fontsize=11, color=COLOR_NAVY)
    ax.set_ylabel("Incident Frequency Density", fontsize=11, color=COLOR_NAVY)
    ax.axvline(log_pwn.median(), color=COLOR_BLUE, linestyle='--', linewidth=2, label=f"Median: 10^{log_pwn.median():.2f} (~{df['PwnCount'].median():,.0f})")
    ax.legend(frameon=True, facecolor='white')
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'pwncount_log_distribution.png'))
    plt.close()
    print("  [+] Saved pwncount_log_distribution.png")

    # 3. breaches_by_year.png (Number of breaches by year)
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    yearly_counts = df['BreachYear'].value_counts().sort_index()
    bars = ax.bar(yearly_counts.index, yearly_counts.values, color=COLOR_VIOLET, alpha=0.85, edgecolor=COLOR_NAVY, width=0.7)
    ax.plot(yearly_counts.index, yearly_counts.values, color=COLOR_BLUE, marker='o', linewidth=2, markersize=5)
    ax.set_title("Annual Cybersecurity Breach Frequency (2007 - 2024)", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Breach Occurrence Year", fontsize=11, color=COLOR_NAVY)
    ax.set_ylabel("Reported Breach Count", fontsize=11, color=COLOR_NAVY)
    ax.set_xticks(yearly_counts.index)
    ax.set_xticklabels(yearly_counts.index, rotation=45)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h}", xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'breaches_by_year.png'))
    plt.close()
    print("  [+] Saved breaches_by_year.png")

    # 4. accounts_affected_by_year.png (Total affected accounts by year)
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    yearly_accounts = (df.groupby('BreachYear')['PwnCount'].sum() / 1e6).sort_index()
    bars = ax.bar(yearly_accounts.index, yearly_accounts.values, color=COLOR_BLUE, alpha=0.85, edgecolor=COLOR_NAVY, width=0.7)
    ax.set_title("Volume of Compromised Accounts by Breach Year (Millions)", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Breach Occurrence Year", fontsize=11, color=COLOR_NAVY)
    ax.set_ylabel("Compromised Accounts (Millions)", fontsize=11, color=COLOR_NAVY)
    ax.set_xticks(yearly_accounts.index)
    ax.set_xticklabels(yearly_accounts.index, rotation=45)
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.annotate(f"{h:,.0f}M", xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'accounts_affected_by_year.png'))
    plt.close()
    print("  [+] Saved accounts_affected_by_year.png")

    # 5. top_15_data_classes.png (Most frequently exposed data classes)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    top_classes = df_classes['DataClass'].value_counts().head(15).sort_values(ascending=True)
    bars = ax.barh(top_classes.index, top_classes.values, color=COLOR_VIOLET, alpha=0.85, edgecolor=COLOR_NAVY)
    ax.set_title("Top 15 Most Frequently Compromised Data Classes", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Number of Breaches Exposing Data Class", fontsize=11, color=COLOR_NAVY)
    for bar in bars:
        w = bar.get_width()
        pct = (w / len(df)) * 100
        ax.annotate(f" {w:,} ({pct:.1f}%)", xy=(w, bar.get_y() + bar.get_height()/2),
                    va='center', fontsize=9, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'top_15_data_classes.png'))
    plt.close()
    print("  [+] Saved top_15_data_classes.png")

    # 6. impact_level_distribution.png (Critical/High/Medium/Low distribution)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    impact_order = ['Critical', 'High', 'Medium', 'Low']
    impact_counts = df['ImpactLevel'].value_counts().reindex(impact_order)
    colors = [PALETTE_IMPACT[imp] for imp in impact_order]
    bars = ax.bar(impact_counts.index, impact_counts.values, color=colors, alpha=0.9, edgecolor=COLOR_NAVY, width=0.6)
    ax.set_title("Analytical Impact Severity Level Distribution", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Severity Classification Tier", fontsize=11, color=COLOR_NAVY)
    ax.set_ylabel("Breach Count", fontsize=11, color=COLOR_NAVY)
    for bar in bars:
        h = bar.get_height()
        pct = (h / len(df)) * 100
        ax.annotate(f"{h:,}\n({pct:.1f}%)", xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'impact_level_distribution.png'))
    plt.close()
    print("  [+] Saved impact_level_distribution.png")

    # 7. boolean_classifications.png (Verified, Sensitive, Malware, Spam, Fabricated, etc.)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    bool_fields = {
        'Verified': df['IsVerified'].sum(),
        'Sensitive': df['IsSensitive'].sum(),
        'Spam List': df['IsSpamList'].sum(),
        'Malware': df['IsMalware'].sum(),
        'Sub-Free': df['IsSubscriptionFree'].sum(),
        'Fabricated': df['IsFabricated'].sum(),
        'Retired': df['IsRetired'].sum()
    }
    bool_s = pd.Series(bool_fields).sort_values(ascending=False)
    bars = ax.bar(bool_s.index, bool_s.values, color=COLOR_BLUE, alpha=0.85, edgecolor=COLOR_NAVY)
    ax.set_title("Cybersecurity Security Flags & Categorization", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_ylabel("Breach Count (Log Scale)", fontsize=11, color=COLOR_NAVY)
    ax.set_yscale('log')
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:,}", xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'boolean_classifications.png'))
    plt.close()
    print("  [+] Saved boolean_classifications.png")

    # 8. time_to_database_addition.png (Intelligence/disclosure latency)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    latency_data = df['DaysToDatabaseAddition'].clip(upper=2000)
    sns.histplot(latency_data, bins=40, kde=True, ax=ax, color=COLOR_VIOLET, edgecolor='white')
    ax.set_title("Intelligence Latency: Days from Breach Occurrence to Database Addition", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Days Elapsed (Capped at 2,000 Days for Visualization)", fontsize=11, color=COLOR_NAVY)
    ax.set_ylabel("Breach Count", fontsize=11, color=COLOR_NAVY)
    med = df['DaysToDatabaseAddition'].median()
    ax.axvline(med, color='#DC2626', linestyle='--', linewidth=2, label=f"Median Latency: {med:.0f} Days (~{med/30.4:.1f} months)")
    ax.legend(frameon=True, facecolor='white')
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'time_to_database_addition.png'))
    plt.close()
    print("  [+] Saved time_to_database_addition.png")

    # 9. correlation_matrix.png (Relevant numerical/Boolean relationships)
    corr_cols = ['PwnCount', 'AffectedAccountsLog', 'DaysToDatabaseAddition', 'BreachYear', 'DataClassCount',
                 'IsVerified', 'IsSensitive', 'IsMalware', 'IsSpamList']
    corr_df = df[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="Purples", ax=ax, cbar_kws={'shrink': 0.8},
                linewidths=0.5, linecolor=COLOR_BORDER)
    ax.set_title("Correlation Matrix of Quantitative Metrics and Security Flags", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'correlation_matrix.png'))
    plt.close()
    print("  [+] Saved correlation_matrix.png")

    # 10. repeated_entities.png (Entities with multiple recorded breaches)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dom_counts = df[df['Domain'] != 'N/A (No Domain / Aggregated Corpus)']['Domain'].value_counts()
    repeat_doms = dom_counts[dom_counts > 1].sort_values(ascending=True)
    bars = ax.barh(repeat_doms.index, repeat_doms.values, color=COLOR_BLUE, alpha=0.85, edgecolor=COLOR_NAVY)
    ax.set_title("Recurrent Organizational Targets: Entities with Multiple Distinct Breaches", fontsize=13, fontweight='bold', color=COLOR_NAVY)
    ax.set_xlabel("Number of Recorded Incidents", fontsize=11, color=COLOR_NAVY)
    ax.set_xticks(range(0, repeat_doms.max() + 2))
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f" {int(w)} breaches", xy=(w, bar.get_y() + bar.get_height()/2),
                    va='center', fontsize=9, fontweight='bold', color=COLOR_NAVY)
    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'repeated_entities.png'))
    plt.close()
    print("  [+] Saved repeated_entities.png")

    print(f"\n[+] All 10 publication-grade figures successfully generated in: {fig_dir}")

if __name__ == '__main__':
    generate_eda_figures()
