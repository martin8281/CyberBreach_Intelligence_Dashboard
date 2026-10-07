# Cybersecurity Data Breach Intelligence - Dataset Quality Audit Report

## Executive Summary

- **Dataset Source**: `breached_services_info.csv`
- **Total Ingested Records**: 777
- **Total Ingested Attributes**: 18
- **Total Compromised User Accounts (`PwnCount`)**: 13,517,282,665
- **Audit Status**: **PASSED WITH ACTIONABLE RECOMMENDATIONS**

---

## 1. Column Inventory & Data Type Profiling

| Column Name | Inferred Type | Null Count | Null % | Unique Values | Whitespace Issues |
|---|---|---|---|---|---|
| `Unnamed: 0` | `int64` | 0 | 0.00% | 777 | 0 |
| `Name` | `object` | 0 | 0.00% | 777 | 0 |
| `Title` | `object` | 0 | 0.00% | 777 | 0 |
| `Domain` | `object` | 38 | 4.89% | 721 | 0 |
| `BreachDate` | `object` | 0 | 0.00% | 650 | 0 |
| `AddedDate` | `object` | 0 | 0.00% | 773 | 0 |
| `ModifiedDate` | `object` | 0 | 0.00% | 768 | 0 |
| `PwnCount` | `int64` | 0 | 0.00% | 776 | 0 |
| `Description` | `object` | 0 | 0.00% | 777 | 3 |
| `LogoPath` | `object` | 0 | 0.00% | 717 | 0 |
| `DataClasses` | `object` | 0 | 0.00% | 401 | 0 |
| `IsVerified` | `bool` | 0 | 0.00% | 2 | 0 |
| `IsFabricated` | `bool` | 0 | 0.00% | 2 | 0 |
| `IsSensitive` | `bool` | 0 | 0.00% | 2 | 0 |
| `IsRetired` | `bool` | 0 | 0.00% | 2 | 0 |
| `IsSpamList` | `bool` | 0 | 0.00% | 2 | 0 |
| `IsMalware` | `bool` | 0 | 0.00% | 2 | 0 |
| `IsSubscriptionFree` | `bool` | 0 | 0.00% | 2 | 0 |

## 2. Missing Value Analysis

- **`Domain` Column**: 38 missing values (4.89%).
  - *Analytical Justification*: Missing domains correspond primarily to aggregated credential stuffing lists, spam lists, malware stealer logs, or untargeted dumps (e.g., `Collection #1`, `Anti Public`, `Naz.API`, `Emotet`). These records MUST NOT be deleted because they account for hundreds of millions of compromised accounts. They will be standardized to `'N/A (No Domain / Aggregated Corpus)'`.
- **All other 17 columns**: 0 missing values (100% complete).

## 3. Duplicate Record Screening

- **Exact Row Duplicates**: 0
- **Content Duplicates (excluding index `Unnamed: 0`)**: 0
- **Unique Breach Identifiers (`Name`)**: 777 unique values across 777 records (100% unique primary key).
- **Unique Domain Names**: 720 unique domains across 739 non-null domain entries. 16 domains appear in multiple distinct historical breaches (e.g., `ogusers.com` has 4 breaches; `linkedin.com` has 3; `twitter.com`, `r2games.com`, `adultfriendfinder.com` each have 2).

## 4. `PwnCount` Distribution & Outlier Diagnostics

The distribution of `PwnCount` exhibits extreme positive right-skewness, typical of power-law cyber incident footprints.

| Metric | Raw Accounts | Log10 Value |
|---|---|---|
| **Minimum** | 858 | 2.93 |
| **5th Percentile** | 30,203 | 4.48 |
| **25th Percentile (Q1)** | 269,552 | 5.43 |
| **Median (50th Percentile)** | 1,141,278 | 6.06 |
| **Mean** | 17,396,760.19 | 7.24 |
| **75th Percentile (Q3)** | 5,970,416 | 6.78 |
| **90th Percentile** | 26,580,827 | 7.42 |
| **95th Percentile** | 72,573,721 | 7.86 |
| **99th Percentile** | 369,139,029 | 8.57 |
| **Maximum** | 772,904,991 | 8.89 |
| **Standard Deviation** | 70,068,864.04 | - |
| **Skewness** | 7.56 | - |
| **Kurtosis** | 65.44 | - |

- **IQR Outliers**: 129 records exceed the statistical upper threshold of 14,521,712 accounts.
  - *Analytical Decision*: In cybersecurity research, large breaches (such as Collection #1 with 772M records, Verifications.io with 763M, and Facebook with 509M) are genuine high-impact mega-breaches, not data entry errors. Therefore, they MUST be retained. Logarithmic scaling ($\log_{10}$) will be applied alongside linear representations to provide accurate comparative visualizations.

## 5. Temporal Validity & Intelligence Latency Audit

| Date Field | Parse Nulls | Earliest Date | Latest Date | Span |
|---|---|---|---|---|
| `BreachDate` | 0 | 2007-07-12 | 2024-05-30 | 16 years |
| `AddedDate` | 0 | 2013-11-30 | 2024-06-03 | 10 years |
| `ModifiedDate` | 0 | 2013-12-04 | 2024-06-03 | 10 years |

- **Temporal Order Integrity (`AddedDate >= BreachDate`)**: 100% valid (0 negative latency instances).
  - **Mean Days to Addition**: 504.9 days (~1.38 years).
  - **Median Days to Addition**: 205 days (~6.8 months).
  - **Maximum Latency**: 4,547 days (~12.5 years, historical breaches disclosed years later).
- **Modification Integrity (`ModifiedDate >= AddedDate`)**: 100% valid (0 negative latency instances).

## 6. Boolean Security Classification Consistency

| Security Flag | True Count | True % | False Count | False % |
|---|---|---|---|---|
| `IsVerified` | 737 | 94.85% | 40 | 5.15% |
| `IsFabricated` | 3 | 0.39% | 774 | 99.61% |
| `IsSensitive` | 61 | 7.85% | 716 | 92.15% |
| `IsRetired` | 1 | 0.13% | 776 | 99.87% |
| `IsSpamList` | 16 | 2.06% | 761 | 97.94% |
| `IsMalware` | 5 | 0.64% | 772 | 99.36% |
| `IsSubscriptionFree` | 6 | 0.77% | 771 | 99.23% |

## 7. DataClasses Structure & Exposure Breakdown

- **Total Unique Data Classes**: 140
- **Average Data Classes per Breach**: 5.33 (Min: 1, Max: 25)
- **Parsing Errors**: 0

### Top 15 Most Frequently Compromised Data Classes

| Rank | Data Class | Breach Count | Exposure % (out of 777) |
|---|---|---|---|
| 1 | **Email addresses** | 771 | 99.23% |
| 2 | **Passwords** | 587 | 75.55% |
| 3 | **Usernames** | 406 | 52.25% |
| 4 | **Names** | 379 | 48.78% |
| 5 | **IP addresses** | 335 | 43.11% |
| 6 | **Phone numbers** | 246 | 31.66% |
| 7 | **Dates of birth** | 211 | 27.16% |
| 8 | **Physical addresses** | 192 | 24.71% |
| 9 | **Genders** | 151 | 19.43% |
| 10 | **Geographic locations** | 108 | 13.90% |
| 11 | **Website activity** | 77 | 9.91% |
| 12 | **Purchases** | 49 | 6.31% |
| 13 | **Social media profiles** | 44 | 5.66% |
| 14 | **Private messages** | 35 | 4.50% |
| 15 | **Job titles** | 29 | 3.73% |

## 8. Justified Data Cleaning Operations

| Operation | Target Field(s) | Justification |
|---|---|---|
| **Drop Index Column** | `Unnamed: 0` | Redundant numeric artifact from CSV serialization. |
| **Whitespace Normalization** | All text fields | Prevent trailing/leading space mismatches in searches and joins. |
| **Missing Domain Imputation** | `Domain` | Substitute null with explicit descriptive string `'N/A (No Domain / Aggregated Corpus)'` without fabricating web domains. |
| **Datetime Standard Parsing** | `BreachDate`, `AddedDate`, `ModifiedDate` | Convert ISO-8601 strings and date strings into unified pandas datetime types. |
| **Feature Engineering** | Date parts, `DaysToDatabaseAddition`, `ImpactLevel` | Enable time-series aggregation, risk segmentation, and latency analysis. |
| **1:N DataClass Normalization** | `DataClasses` | Decouple composite arrays into `breach_data_classes.csv` to prevent double-counting breaches while enabling exact data type threat modeling. |
