"""
02_data_cleaning.py - Data Cleaning, Feature Engineering & SQLite Database Pipeline
Author: Cybersecurity Analytics Team
"""

import os
import ast
import sqlite3
import numpy as np
import pandas as pd

def clean_and_transform():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, 'data', 'breached_services_info.csv')
    cleaned_path = os.path.join(base_dir, 'data', 'cleaned_breach_data.csv')
    classes_path = os.path.join(base_dir, 'data', 'breach_data_classes.csv')
    db_path = os.path.join(base_dir, 'data', 'breaches.db')

    print(f"[*] Reading raw dataset from: {raw_path}")
    df = pd.read_csv(raw_path)

    # 1. Drop serial index artifact
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)
        print("  [+] Dropped redundant 'Unnamed: 0' index column.")

    # 2. Text sanitization & whitespace stripping
    text_cols = ['Name', 'Title', 'Domain', 'Description', 'LogoPath']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    print("  [+] Trimmed whitespace across string attributes.")

    # 3. Standardize missing Domains
    df['Domain'] = df['Domain'].replace({'nan': 'N/A (No Domain / Aggregated Corpus)', '': 'N/A (No Domain / Aggregated Corpus)'})
    print("  [+] Standardized missing domains to 'N/A (No Domain / Aggregated Corpus)'.")

    # 4. Datetime parsing
    df['BreachDate'] = pd.to_datetime(df['BreachDate'], errors='coerce')
    df['AddedDate'] = pd.to_datetime(df['AddedDate'], errors='coerce')
    df['ModifiedDate'] = pd.to_datetime(df['ModifiedDate'], errors='coerce')

    # 5. Validate PwnCount numeric integrity
    df['PwnCount'] = pd.to_numeric(df['PwnCount'], errors='coerce').fillna(0).astype('int64')

    # 6. Standardize Booleans
    bool_cols = ['IsVerified', 'IsFabricated', 'IsSensitive', 'IsRetired', 'IsSpamList', 'IsMalware', 'IsSubscriptionFree']
    for col in bool_cols:
        df[col] = df[col].astype(bool)

    # 7. Date Feature Engineering
    df['BreachYear'] = df['BreachDate'].dt.year.astype(int)
    df['BreachMonth'] = df['BreachDate'].dt.month.astype(int)
    df['BreachMonthName'] = df['BreachDate'].dt.strftime('%B')
    df['BreachQuarter'] = df['BreachDate'].dt.quarter.astype(int)
    df['BreachDay'] = df['BreachDate'].dt.day.astype(int)
    df['BreachDayOfWeek'] = df['BreachDate'].dt.strftime('%A')

    # Latency Features
    added_date_utc = df['AddedDate'].dt.tz_localize(None) if df['AddedDate'].dt.tz is not None else df['AddedDate']
    breach_date_utc = df['BreachDate'].dt.tz_localize(None) if df['BreachDate'].dt.tz is not None else df['BreachDate']
    modified_date_utc = df['ModifiedDate'].dt.tz_localize(None) if df['ModifiedDate'].dt.tz is not None else df['ModifiedDate']

    df['DaysToDatabaseAddition'] = (added_date_utc - breach_date_utc).dt.days.clip(lower=0).fillna(0).astype(int)
    df['DaysSinceModification'] = (modified_date_utc - added_date_utc).dt.total_seconds() / 86400.0
    df['DaysSinceModification'] = df['DaysSinceModification'].clip(lower=0).round(2)
    
    current_year = 2026
    df['BreachAgeYears'] = (current_year - df['BreachYear']).clip(lower=0)

    # 8. Numeric Log Transformations (keep both PwnCount and AffectedAccountsLog)
    df['AffectedAccountsLog'] = np.log10(df['PwnCount'].replace(0, 1)).round(4)

    # 9. Analytical ImpactLevel Classification
    def classify_impact(count):
        if count >= 10_000_000:
            return 'Critical'
        elif count >= 1_000_000:
            return 'High'
        elif count >= 100_000:
            return 'Medium'
        else:
            return 'Low'

    df['ImpactLevel'] = df['PwnCount'].apply(classify_impact)

    # 10. Status Feature Labels
    df['VerificationStatus'] = df['IsVerified'].map({True: 'Verified', False: 'Unverified'})
    df['SensitivityStatus'] = df['IsSensitive'].map({True: 'Sensitive', False: 'Standard'})
    df['MalwareStatus'] = df['IsMalware'].map({True: 'Malware-Associated', False: 'Standard'})

    # 11. Parse and count DataClasses
    data_class_rows = []
    class_count_col = []

    for idx, row in df.iterrows():
        raw_val = row['DataClasses']
        try:
            parsed = ast.literal_eval(raw_val) if isinstance(raw_val, str) else []
        except Exception:
            parsed = []
        
        class_count_col.append(len(parsed))
        for cls_item in parsed:
            data_class_rows.append({
                'BreachName': row['Name'],
                'Title': row['Title'],
                'DataClass': cls_item.strip(),
                'PwnCount': row['PwnCount'],
                'BreachYear': row['BreachYear'],
                'ImpactLevel': row['ImpactLevel'],
                'IsVerified': row['IsVerified'],
                'IsSensitive': row['IsSensitive']
            })

    df['DataClassCount'] = class_count_col
    df_classes = pd.DataFrame(data_class_rows)

    # Save cleaned datasets
    print(f"[*] Saving cleaned dataset to: {cleaned_path}")
    df.to_csv(cleaned_path, index=False)

    print(f"[*] Saving normalized DataClasses dataset ({len(df_classes):,} rows) to: {classes_path}")
    df_classes.to_csv(classes_path, index=False)

    # 12. SQLite Database Population with required indexes
    print(f"[*] Loading datasets into SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    
    df_sqlite = df.copy()
    df_sqlite['BreachDate'] = df_sqlite['BreachDate'].dt.strftime('%Y-%m-%d')
    df_sqlite['AddedDate'] = df_sqlite['AddedDate'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df_sqlite['ModifiedDate'] = df_sqlite['ModifiedDate'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    df_sqlite.to_sql('breaches', conn, if_exists='replace', index=False)
    df_classes.to_sql('breach_data_classes', conn, if_exists='replace', index=False)

    # Create analytical indexes on Name, Domain, BreachDate, BreachYear, ImpactLevel
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_name ON breaches(Name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_domain ON breaches(Domain);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_date ON breaches(BreachDate);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_year ON breaches(BreachYear);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_impact ON breaches(ImpactLevel);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_verified ON breaches(IsVerified);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_breach_sensitive ON breaches(IsSensitive);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dataclass_name ON breach_data_classes(BreachName);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dataclass_class ON breach_data_classes(DataClass);")
    conn.commit()
    conn.close()

    print("\n[+] Data pipeline completed successfully!")
    print(f"  - Total Breaches Processed: {len(df):,}")
    print(f"  - Total Accounts Compromised: {df['PwnCount'].sum():,}")
    print(f"  - Total Normalized DataClass Records: {len(df_classes):,}")

if __name__ == '__main__':
    clean_and_transform()
