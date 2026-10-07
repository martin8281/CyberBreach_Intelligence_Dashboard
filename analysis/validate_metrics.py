"""
validate_metrics.py - Verification & Numerical Reconciliation Test Suite
Author: Cybersecurity Analytics Team
"""

import os
import sqlite3
import pandas as pd

def run_validation():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, 'data', 'breached_services_info.csv')
    cleaned_path = os.path.join(base_dir, 'data', 'cleaned_breach_data.csv')
    classes_path = os.path.join(base_dir, 'data', 'breach_data_classes.csv')
    db_path = os.path.join(base_dir, 'data', 'breaches.db')

    print("=" * 60)
    print("CYBERSECURITY METRICS & DATA RECONCILIATION AUDIT")
    print("=" * 60)

    raw_df = pd.read_csv(raw_path)
    clean_df = pd.read_csv(cleaned_path)
    classes_df = pd.read_csv(classes_path)
    
    conn = sqlite3.connect(db_path)
    db_breaches = pd.read_sql("SELECT * FROM breaches", conn)
    db_classes = pd.read_sql("SELECT * FROM breach_data_classes", conn)
    conn.close()

    # 1. Row Counts
    print(f"\n1. ROW COUNTS:")
    print(f"  - Raw Dataset Rows:     {len(raw_df):,}")
    print(f"  - Cleaned Dataset Rows: {len(clean_df):,}")
    print(f"  - SQLite Breaches Rows: {len(db_breaches):,}")
    assert len(raw_df) == len(clean_df) == len(db_breaches) == 777, "Row count mismatch!"
    print("  [OK] Row counts reconciled: exactly 777 records.")

    # 2. PwnCount Sum, Max, Mean, Median
    print(f"\n2. PWNCOUNT ACCURACY:")
    raw_sum = int(raw_df['PwnCount'].sum())
    clean_sum = int(clean_df['PwnCount'].sum())
    db_sum = int(db_breaches['PwnCount'].sum())
    print(f"  - Raw PwnCount Sum:     {raw_sum:,}")
    print(f"  - Cleaned PwnCount Sum: {clean_sum:,}")
    print(f"  - SQLite PwnCount Sum:  {db_sum:,}")
    assert raw_sum == clean_sum == db_sum, "PwnCount sum mismatch!"
    print(f"  [OK] Total Compromised Accounts reconciled: {clean_sum:,}")

    clean_max = int(clean_df['PwnCount'].max())
    clean_mean = float(clean_df['PwnCount'].mean())
    clean_median = float(clean_df['PwnCount'].median())
    print(f"  - Max Breach Size:      {clean_max:,} ({clean_df.loc[clean_df['PwnCount'].idxmax()]['Title']})")
    print(f"  - Mean Breach Size:     {clean_mean:,.2f}")
    print(f"  - Median Breach Size:   {clean_median:,.0f}")

    # 3. Security Flags
    print(f"\n3. SECURITY FLAGS RECONCILIATION:")
    flags = ['IsVerified', 'IsSensitive', 'IsMalware', 'IsSpamList', 'IsFabricated', 'IsRetired', 'IsSubscriptionFree']
    for f in flags:
        raw_cnt = int(raw_df[f].astype(bool).sum())
        clean_cnt = int(clean_df[f].astype(bool).sum())
        assert raw_cnt == clean_cnt, f"Flag {f} count mismatch!"
        print(f"  - {f:<20}: {clean_cnt:>4} records ({clean_cnt/len(clean_df)*100:.1f}%)")
    print("  [OK] All 7 security flags reconciled perfectly.")

    # 4. Impact Levels
    print(f"\n4. IMPACT LEVEL BREAKDOWN:")
    impact_dist = clean_df['ImpactLevel'].value_counts().to_dict()
    for imp in ['Critical', 'High', 'Medium', 'Low']:
        print(f"  - {imp:<10}: {impact_dist.get(imp, 0):>4} breaches ({impact_dist.get(imp, 0)/len(clean_df)*100:.1f}%)")
    assert sum(impact_dist.values()) == 777, "Impact level sum mismatch!"
    print("  [OK] Impact tiers sum to exactly 777.")

    # 5. DataClasses Normalization
    print(f"\n5. DATACLASSES NORMALIZATION (NO DOUBLE COUNTING):")
    print(f"  - Total Normalized Relations: {len(classes_df):,}")
    print(f"  - Unique Data Classes:        {classes_df['DataClass'].nunique()}")
    print(f"  - Distinct Breaches in Norm:  {classes_df['BreachName'].nunique()}")
    assert classes_df['BreachName'].nunique() == 777, "Not all breaches normalized!"
    print("  [OK] 100% of breaches represented without inflating breach incident count.")

    print("\n" + "=" * 60)
    print("ALL VERIFICATION CHECKS PASSED WITH 100% RECONCILIATION!")
    print("=" * 60)

if __name__ == '__main__':
    run_validation()
