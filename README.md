# CyberBreach Intel: Cybersecurity Data Breach Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14+-violet.svg)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.14+-blue.svg)](https://plotly.com/)
[![Bootstrap](https://img.shields.io/badge/Theme-Enterprise%20Light-6D28D9.svg)](#)

A research-ready, interactive cybersecurity threat intelligence and data breach analytics platform built with **Python**, **Pandas**, **Plotly**, **Dash**, and **Dash Bootstrap Components**.

---

## 1. Project Objective

The primary objective of **CyberBreach Intel** is to provide an enterprise-grade, academic-caliber analytics system to investigate, quantify, and visualize historical cybersecurity data breaches. The platform empowers cybersecurity researchers, incident responders, and compliance officers to:
- Track breach frequency trajectories and cumulative incident momentum over time.
- Analyze the scale of compromised identity accounts across logarithmic and linear distributions.
- Uncover high-risk exposed data assets (e.g., plain-text passwords, hashed credentials, usernames, PII, financial data).
- Dissect security classifications (Verified vs. Unverified, Sensitive Risk, Malware-associated Stealers, Aggregated Spam Lists, and Fabricated/disputed claims).
- Investigate recurrent organizational targets that have suffered multiple distinct historical breaches.
- Search and drill down into individual breach incidents via a searchable and exportable intelligence explorer.

---

## 2. Dataset Description

The dataset source (`breached_services_info.csv`) captures 777 cybersecurity breach incidents spanning from 2007 through 2024, accounting for **13,517,282,665** (13.52 billion) compromised user accounts.

### Data Dictionary

| Column Name | Type | Description | Completeness |
|---|---|---|---|
| `Name` | `string` | Unique alphanumeric identifier / slug for the breach event. | 100% (777 unique) |
| `Title` | `string` | Human-readable title of the compromised service or organization. | 100% |
| `Domain` | `string` | Internet domain name of the victim service (or `N/A` for aggregated dumps). | 95.11% (38 nulls) |
| `BreachDate` | `date` | Approximate date when the security incident occurred (`YYYY-MM-DD`). | 100% |
| `AddedDate` | `datetime` | ISO-8601 UTC timestamp when the breach was ingested into the intelligence database. | 100% |
| `ModifiedDate` | `datetime` | ISO-8601 UTC timestamp when the breach record was last updated or verified. | 100% |
| `PwnCount` | `int64` | Total number of unique user accounts compromised in the incident. | 100% (Min: 858, Max: 772.9M) |
| `Description` | `string` | Detailed narrative outlining the threat vector, leak circumstances, and impact. | 100% |
| `LogoPath` | `string` | URI to the victim entity's official emblem/logo. | 100% |
| `DataClasses` | `string` | Python stringified array of exposed data categories (e.g., Passwords, Emails). | 100% (140 unique classes) |
| `IsVerified` | `bool` | `True` if the breach data was authenticated against known user subscriber bases. | 737 True / 40 False |
| `IsFabricated` | `bool` | `True` if the alleged breach was discredited or determined to be fabricated. | 3 True / 774 False |
| `IsSensitive` | `bool` | `True` if breach exposes sensitive personal life data (e.g., adult sites, healthcare). | 61 True / 716 False |
| `IsRetired` | `bool` | `True` if the breach has been retired or consolidated into other records. | 1 True / 776 False |
| `IsSpamList` | `bool` | `True` if the breach originates from a marketing spam list / data scraper. | 16 True / 761 False |
| `IsMalware` | `bool` | `True` if the data was exfiltrated directly via malware stealer logs / botnets. | 5 True / 772 False |
| `IsSubscriptionFree` | `bool` | `True` if the breach data is provided to domain administrators free of charge. | 6 True / 771 False |

---

## 3. Data Cleaning & Transformation Methodology

All data cleaning operations are justified based on statistical, domain, and data-quality standards:
1. **Preservation of Raw Data**: The original `data/breached_services_info.csv` is preserved without destructive in-place alterations.
2. **Index Artifact Removal**: Dropped the redundant exported serial index column `Unnamed: 0`.
3. **Whitespace Standardization**: Trimmed leading and trailing whitespace across all string columns to prevent search misses.
4. **Missing Domain Imputation**: 38 records lack a specific web domain because they represent credential stuffing combo lists, stealer logs, or spam botnet dumps (e.g., `Collection #1`, `Naz.API`, `Emotet`). These records were **retained** to preserve over 2.5 billion affected accounts and standardized to `'N/A (No Domain / Aggregated Corpus)'`.
5. **Datetime Conversions**: Converted `BreachDate`, `AddedDate`, and `ModifiedDate` into timezone-aware and UTC pandas `datetime64[ns]` objects.

---

## 4. Feature Engineering

To facilitate research-grade threat modeling, the following analytical features were engineered:

### Temporal Analytics
- **`BreachYear`**, **`BreachMonth`**, **`BreachMonthName`**, **`BreachQuarter`**, **`BreachDay`**, **`BreachDayOfWeek`**: Temporal components enabling cyclical and seasonal incident analysis.
- **`DaysToDatabaseAddition`**: $(\text{AddedDate} - \text{BreachDate})_{\text{days}}$ measuring **intelligence disclosure latency** (the elapsed time between breach occurrence and public intelligence cataloging). The median latency is **205 days (~6.8 months)**, highlighting significant delayed detection.
- **`DaysSinceModification`**: Elapsed days between cataloging and record updates.
- **`BreachAgeYears`**: Elapsed years from incident occurrence to present.

### Account Footprint Scaling
- **`AffectedAccountsLog`**: $\log_{10}(\text{PwnCount})$ to compress extreme positive skewness (ranging from 858 accounts to 772.9 million).

### Analytical `ImpactLevel` Risk Classification
An analytical severity tier based on compromised account volume (explicitly documented as an analytical categorization rather than a source dataset classification):
- **Critical** ($\ge 10,000,000$ accounts): 144 breaches (18.5%)
- **High** ($1,000,000 \le \text{PwnCount} < 10,000,000$ accounts): 263 breaches (33.8%)
- **Medium** ($100,000 \le \text{PwnCount} < 1,000,000$ accounts): 258 breaches (33.2%)
- **Low** ($< 100,000$ accounts): 112 breaches (14.4%)

### 1:N DataClasses Normalization
Composite `DataClasses` strings were parsed and decoupled into `data/breach_data_classes.csv` (4,143 records across 140 unique classes). This allows exact aggregation of compromised data types without double-counting breach incidents.

---

## 5. SQLite Database Integration

The system populates a relational database `data/breaches.db` containing:
- Table `breaches`: complete breach records with analytical indexes on `Name`, `BreachYear`, `ImpactLevel`, `IsVerified`, and `IsSensitive`.
- Table `breach_data_classes`: normalized relational mapping with indexes on `BreachName` and `DataClass`.

---

## 6. Dashboard Architecture & Features

The dashboard is built with a light-mode **White + Violet + Dark Blue** cybersecurity aesthetic:
- **Palette**: Background `#FFFFFF`, Secondary Surface `#F8FAFC`, Deep Navy `#0F172A`, Deep Violet `#6D28D9`, Cobalt Blue `#1D4ED8`, Light Violet `#EDE9FE`, Neutral Border `#E2E8F0`.

### Navigation & Views
1. **Executive Overview**:
   - 8 Dynamic KPI Cards (Total Incidents, Accounts Compromised, Mean Size, Max Footprint, Verified Count, Sensitive Count, Malware Count, Critical/High Impact Count).
   - Time Series Line & Area Chart (Annual Incidents & Cumulative Progression).
   - Annual Exposed Accounts Bar Chart with Linear/Log10 scale toggle.
   - Top 10 Largest Breaches leaderboard.
   - Analytical Impact Severity donut chart.
   - Intelligence Latency distribution histogram.
2. **Breach Intelligence**:
   - Top 15/20 Compromised Data Classes frequency analysis.
   - Security Flags breakdown (Verified, Sensitive, Malware, Spam, Fabricated).
   - Deep Dive Threat Intelligence Dossiers:
     - Malware Stealer botnet analysis (Emotet, Qakbot, RedLine, pcTattletale).
     - Marketing Spam & Credential Dumps (River City Media, Onliner Spambot).
     - Fabricated Corpuses (Paytm, Zoosk 2011, JustDate forensic scrutiny).
3. **Entity Analysis**:
   - High-Target Re-occurrence leaderboard (organizations with 2+ breaches).
   - Entity Search dropdown with instant auto-complete and Quick Selection shortcuts (Adobe, LinkedIn, Twitter, Facebook, Dropbox, Canva).
   - Selected Entity Intelligence Dossier: Key metrics, security badges, incident timeline, exposed data classes badge cloud, and sanitized HTML narrative.
4. **Breach Explorer**:
   - Searchable, sortable, and paginated (15/page) interactive data table.
   - Click-to-Inspect row selection: displays a complete incident dossier card below without cluttering table rows.
   - CSV Export button: directly exports currently filtered data subsets to `cybersecurity_breaches_export.csv`.
5. **Global Filtering Pipeline**:
   - Year Range Slider (2007 - 2024).
   - Impact Level Multi-Select.
   - Verification Status filter (All, Verified, Unverified).
   - Sensitivity Status filter.
   - Reset Filters button.

---

## 7. Technology Stack

- **Python 3.11+**
- **Pandas**: Ingestion, cleaning, feature engineering, and relational transformations.
- **NumPy**: Statistical aggregations and logarithmic transformations.
- **Matplotlib & Seaborn**: Statistical exploratory data analysis and figure exports.
- **Plotly**: Responsive, interactive SVG/WebGL data visualizations.
- **Dash & Dash Bootstrap Components**: Reactive multi-page web application.
- **SQLite3**: Relational database storage with custom indexes.

---

## 8. Installation & Setup

### 1. Clone or Navigate to the Repository
```bash
cd "c:\Users\Admin\CHRIST\S3\DAS\DAS Mini project"
```

### 2. Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 9. How to Run

### Step 1: Run the Data Quality Audit
Generates `outputs/data_quality_report.md`:
```bash
python analysis/01_data_audit.py
```

### Step 2: Run Data Cleaning & Database Pipeline
Generates `data/cleaned_breach_data.csv`, `data/breach_data_classes.csv`, and `data/breaches.db`:
```bash
python analysis/02_data_cleaning.py
```

### Step 3: Run Exploratory Data Analysis
Generates 9 high-resolution publication figures in `outputs/figures/`:
```bash
python analysis/03_eda.py
```

### Step 4: Verify Calculations & Numerical Reconciliation
```bash
python analysis/validate_metrics.py
```

### Step 5: Launch the Interactive Dashboard
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:8050/
```

---

## 10. Project Structure

```
DAS Mini project/
├── data/
│   ├── breached_services_info.csv        # Original raw source dataset
│   ├── cleaned_breach_data.csv           # Cleaned & feature-engineered dataset
│   ├── breach_data_classes.csv           # Normalized 1:N DataClasses relational table
│   └── breaches.db                       # Indexed SQLite relational database
├── analysis/
│   ├── 01_data_audit.py                  # Automated data audit & quality report generator
│   ├── 02_data_cleaning.py               # Data cleaning, feature engineering & DB loader
│   ├── 03_eda.py                         # Statistical EDA & figure generator
│   └── validate_metrics.py               # Automated reconciliation test suite
├── dashboard/
│   ├── __init__.py
│   ├── app.py                            # Dash application factory & runner
│   ├── config.py                         # Theme palette, constants, helpers & data loaders
│   ├── layout.py                         # Multi-page layouts (Overview, Intelligence, Entity, Explorer)
│   ├── callbacks.py                      # Reactive Dash callbacks for filtering, search, and export
│   └── charts.py                         # Plotly figure factories
├── assets/
│   └── style.css                         # Enterprise Light theme styling
├── outputs/
│   ├── figures/                          # Publication-grade PNG charts (300 DPI)
│   └── data_quality_report.md            # Comprehensive data audit report
├── app.py                                # Root entrypoint to run the dashboard
├── requirements.txt                      # Pinned Python package dependencies
└── README.md                             # Project documentation
```

---

## 11. Key Analytical Findings

1. **Massive Concentration in Email & Password Exposure**: 771 breaches (99.2%) exposed email addresses, and 587 breaches (75.5%) exposed user passwords.
2. **Extreme Disclosure Latency**: The median intelligence latency from breach date to cataloging is **205 days**, with 25% of breaches taking over **721 days (~2 years)** before public disclosure.
3. **Power-Law Incident Impact**: While the median breach involves 1.14 million accounts, the mean is 17.4 million, driven by mega-breaches such as Collection #1 (772.9M), Verifications.io (763.1M), and Facebook (509.5M).
4. **Target Re-occurrence**: Multiple entities have experienced repeated compromises (e.g., `ogusers.com` with 4 separate incidents; `linkedin.com` with 3 incidents; `twitter.com`, `r2games.com`, and `adultfriendfinder.com` with 2 incidents each).
5. **Rise of Info-Stealer Malware**: Distinct campaigns like RedLine Stealer, Qakbot, and Emotet highlight the shift from perimeter penetration to client-side credential extraction.

---

## 12. Limitations & Future Work

- **Self-Reported Incident Dates**: The exact timestamp of initial intrusion is often an approximation based on threat actor forum disclosures.
- **De-duplication Between Corpuses**: Massive credential combo lists often aggregate earlier historical breaches.
- **Future Improvements**:
  - Implement real-time threat intelligence feeds via HaveIBeenPwned API v3.
  - Add password hashing algorithm vulnerability profiling (MD5, SHA1 vs bcrypt, Argon2).
  - Train machine learning classification models to forecast breach impact severity based on early incident attributes.
#   C y b e r B r e a c h _ I n t e l l i g e n c e _ D a s h b o a r d  
 