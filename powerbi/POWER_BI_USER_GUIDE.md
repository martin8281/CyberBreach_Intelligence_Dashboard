# CyberBreach Intel: Power BI Deployment & User Guide

**Project:** Cybersecurity Data Breach Intelligence Platform (DAS Mini Project)  
**Author:** Cybersecurity Analytics & Data Engineering Team  
**Artifacts Generated:**
- **Power BI Template File:** `CyberBreach_Intelligence_Dashboard.pbit`
- **Power BI Project File:** `CyberBreach_Intelligence.pbip`
- **Report Definition:** `CyberBreach_Intelligence.Report/`
- **Semantic Model (TMSL):** `CyberBreach_Intelligence.SemanticModel/`
- **Enterprise Theme:** `powerbi/CyberBreach_Enterprise_Theme.json`
- **DAX Measures Library:** `powerbi/dax_measures.dax`
- **Power Query M Script:** `powerbi/power_query_transformations.m`

---

## 1. Quick Start: How to Open the Power BI Solution

You have two native options to launch this dashboard in **Power BI Desktop**:

### Option A: Open the Compiled Template (`.pbit`) — Recommended for Instant Setup
1. Locate the file:
   ```
   CyberBreach_Intelligence_Dashboard.pbit
   ```
   *(Located in the project root folder)*.
2. **Double-click** the `.pbit` file.
3. Power BI Desktop will launch automatically.
4. When prompted, Power BI will execute the embedded Power Query (M) transformations, import `cleaned_breach_data.csv` (777 records) and `breach_data_classes.csv` (4,143 records), compile the VertiPaq database in memory, and load all 4 visual report pages.
5. Click **File > Save As** and save as `CyberBreach_Intelligence.pbix` to store your local report with cached data.

### Option B: Open the Power BI Project (`.pbip`) — Recommended for Fabric & Git Integration
1. Locate the project file:
   ```
   CyberBreach_Intelligence.pbip
   ```
   *(Located in the project root folder)*.
2. **Double-click** `CyberBreach_Intelligence.pbip`.
3. Power BI Desktop will open the modular project directly, linking the `Report` visual definitions with the `SemanticModel` TMSL schema.

---

## 2. Data Model Architecture & Relationships

The Power BI semantic model connects two tables in a star/snowflake schema:

```
+------------------------------------+              +------------------------------------+
|         CleanedBreachData          | 1          N |         BreachDataClasses          |
+------------------------------------+--------------+------------------------------------+
| [PK] Name (Primary Key)            | <----------  | [FK] BreachName (Foreign Key)      |
| Title                              |              | Title                              |
| Domain                             |              | DataClass (e.g. Passwords, Emails) |
| BreachDate                         |              | PwnCount                           |
| AddedDate                          |              | BreachYear                         |
| ModifiedDate                       |              | ImpactLevel                        |
| PwnCount                           |              | IsVerified                         |
| ImpactLevel (Critical, High, ...)  |              | IsSensitive                        |
| IsVerified, IsSensitive, IsMalware |              +------------------------------------+
| DaysToDatabaseAddition (Latency)   |
| BreachYear, BreachMonth, etc.      |
+------------------------------------+
```

- **Primary Table**: `CleanedBreachData` (777 rows, 32 columns).
- **Secondary Normalized Table**: `BreachDataClasses` (4,143 rows, 8 columns).
- **Cardinality**: `1 to Many (1:*)` from `CleanedBreachData[Name]` to `BreachDataClasses[BreachName]`.
- **Cross-Filter Direction**: Single (CleanedBreachData filters BreachDataClasses).
- **Integrity Rule**: Always use `[Total Breaches]` from `CleanedBreachData` to calculate incident counts to prevent double-counting.

---

## 3. Core DAX Measures Reference

All measures are implemented inside the model and exported in `powerbi/dax_measures.dax`:

### A. Core Volume Metrics
```dax
Total Breaches = COUNTROWS('CleanedBreachData')
```
```dax
Total Accounts Compromised = SUM('CleanedBreachData'[PwnCount])
```
```dax
Average Breach Size = AVERAGE('CleanedBreachData'[PwnCount])
```
```dax
Median Breach Size = MEDIAN('CleanedBreachData'[PwnCount])
```
```dax
Largest Single Breach = MAX('CleanedBreachData'[PwnCount])
```

### B. Security Classification Metrics
```dax
Verified Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsVerified] = TRUE())
```
```dax
% Verified Breaches = DIVIDE([Verified Breaches], [Total Breaches], 0)
```
```dax
Sensitive Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsSensitive] = TRUE())
```
```dax
% Sensitive Breaches = DIVIDE([Sensitive Breaches], [Total Breaches], 0)
```
```dax
Malware-Associated Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsMalware] = TRUE())
```
```dax
Spam List Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsSpamList] = TRUE())
```
```dax
Fabricated Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsFabricated] = TRUE())
```

### C. Severity Tier Metrics
```dax
Critical Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] = "Critical")
```
```dax
High Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] = "High")
```
```dax
Critical & High Breaches = CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] IN {"Critical", "High"})
```

### D. Intelligence Latency Metrics
```dax
Mean Intelligence Latency Days = AVERAGE('CleanedBreachData'[DaysToDatabaseAddition])
```
```dax
Median Intelligence Latency Days = MEDIAN('CleanedBreachData'[DaysToDatabaseAddition])
```

---

## 4. Multi-Page Report Layout & Visual Specifications

### Page 1: Executive Overview
- **Header**: "CYBERSECURITY DATA BREACH INTELLIGENCE — EXECUTIVE OVERVIEW"
- **8 KPI Cards**: Total Breaches, Total Accounts Compromised, Average Breach Size, Largest Single Breach, Verified Breaches, Sensitive Breaches, Malware-Associated Breaches, Critical & High Breaches.
- **Visual 1 (Line/Area Chart)**: Annual Incident Frequency & Cumulative Progression (`BreachYear` vs `[Total Breaches]`).
- **Visual 2 (Column Chart)**: Total Accounts Compromised by Year (`BreachYear` vs `[Total Accounts Compromised]`).
- **Visual 3 (Clustered Bar Chart)**: Top 10 Largest Breaches (`Title` vs `[Total Accounts Compromised]`).
- **Visual 4 (Donut Chart)**: Impact-Level Severity Distribution (`ImpactLevel` vs `[Total Breaches]`).
- **Slicers**: `BreachYear` range slider, `ImpactLevel` multi-select, and `VerificationStatus` toggle.

### Page 2: Breach Intelligence
- **Header**: "BREACH INTELLIGENCE & THREAT ASSET EXPOSURE"
- **Visual 1 (Clustered Bar Chart)**: Top 20 Exposed Data Classes from `BreachDataClasses[DataClass]`.
- **Visual 2 (Column Chart)**: Security Classification Breakdown (Verified vs Unverified).
- **Visual 3 (Histogram / Column Chart)**: Intelligence Latency Distribution (`DaysToDatabaseAddition` vs `[Total Breaches]`).
- **KPI Indicators**: Median Latency Days (205 days) and Mean Latency Days (504.9 days).

### Page 3: Entity Intelligence
- **Header**: "ENTITY INTELLIGENCE & TARGET RE-OCCURRENCE ANALYSIS"
- **Slicer**: Searchable Organization / Entity selector (`CleanedBreachData[Title]`).
- **Visual 1 (Clustered Bar Chart)**: Recurrent Targets (Organizations with 2+ breaches: `ogusers.com`, `linkedin.com`, `twitter.com`, `r2games.com`, `cardmafia.cc`, `adultfriendfinder.com`).
- **Visual 2 (Line / Scatter Chart)**: Incident Timeline (`BreachDate` vs `[Total Accounts Compromised]`).

### Page 4: Breach Explorer
- **Header**: "SEARCHABLE BREACH INCIDENT CATALOG & EXPLORER"
- **Visual 1 (Interactive Table)**: Columns for `Name`, `Title`, `Domain`, `BreachDate`, `PwnCount`, `ImpactLevel`, `VerificationStatus`, and `SensitivityStatus`.
- **Slicers**: Interactive filters for `ImpactLevel`, `VerificationStatus`, and `BreachYear`.

---

## 5. Enterprise Color Theme Palette

The visual design implements the **Enterprise Light Mode** palette:
- **Canvas Background**: `#F8FAFC` (Slate 50)
- **Card Background**: `#FFFFFF`
- **Card Borders**: `#E2E8F0`
- **Primary Text**: `#0F172A` (Navy/Slate 900)
- **Primary Accent**: `#6D28D9` (Deep Violet)
- **Secondary Accent**: `#1D4ED8` (Cobalt Blue)
- **Risk Severity Colors**:
  - **Critical**: `#DC2626` (Red)
  - **High**: `#EA580C` (Orange)
  - **Medium**: `#D97706` (Amber)
  - **Low**: `#16A34A` (Green)
  - **Verified**: `#0D9488` (Teal)
