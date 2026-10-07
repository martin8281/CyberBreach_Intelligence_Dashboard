"""
generate_powerbi_solution.py - Automated Power BI Artifacts & Model Factory
Author: Cybersecurity Analytics & Data Engineering Team
"""

import os
import json
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CLEANED_CSV = os.path.join(DATA_DIR, 'cleaned_breach_data.csv').replace('\\', '/')
CLASSES_CSV = os.path.join(DATA_DIR, 'breach_data_classes.csv').replace('\\', '/')

PBIP_ROOT = os.path.join(BASE_DIR, 'CyberBreach_Intelligence.pbip')
REPORT_DIR = os.path.join(BASE_DIR, 'CyberBreach_Intelligence.Report')
MODEL_DIR = os.path.join(BASE_DIR, 'CyberBreach_Intelligence.SemanticModel')
PBIT_PATH = os.path.join(BASE_DIR, 'CyberBreach_Intelligence_Dashboard.pbit')

def create_visual_json(name, vtype, x, y, w, h, tab_order, projections=None, title=None):
    vis = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": tab_order * 10,
            "height": h,
            "width": w,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": vtype
        }
    }
    if projections:
        vis["visual"]["query"] = {
            "queryState": projections
        }
    if title:
        vis["visual"]["objects"] = {
            "title": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                    }
                }
            ]
        }
    return vis

def generate_pbip_solution():
    print("[*] Generating Power BI Project (.pbip) & Template (.pbit)...")

    # 1. Clean / create directories
    for d in [REPORT_DIR, MODEL_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # 2. CyberBreach_Intelligence.pbip root pointer
    pbip_data = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "CyberBreach_Intelligence.Report"
                }
            }
        ],
        "settings": {}
    }
    with open(PBIP_ROOT, 'w', encoding='utf-8') as f:
        json.dump(pbip_data, f, indent=2)
    print(f"  [+] Created {PBIP_ROOT}")

    # 3. SemanticModel/definition.pbism
    with open(os.path.join(MODEL_DIR, 'definition.pbism'), 'w', encoding='utf-8') as f:
        json.dump({"version": "1.0"}, f, indent=2)

    # 4. SemanticModel/model.bim
    m_query_breaches = f"""let
    Source = Csv.Document(File.Contents("{CLEANED_CSV}"),[Delimiter=",", Columns=32, Encoding=65001, QuoteStyle=QuoteStyle.Rfc1208]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{
        {{"Name", type text}}, {{"Title", type text}}, {{"Domain", type text}},
        {{"BreachDate", type date}}, {{"AddedDate", type datetimezone}}, {{"ModifiedDate", type datetimezone}},
        {{"PwnCount", Int64.Type}}, {{"Description", type text}}, {{"LogoPath", type text}},
        {{"DataClasses", type text}}, {{"IsVerified", type logical}}, {{"IsFabricated", type logical}},
        {{"IsSensitive", type logical}}, {{"IsRetired", type logical}}, {{"IsSpamList", type logical}},
        {{"IsMalware", type logical}}, {{"IsSubscriptionFree", type logical}},
        {{"BreachYear", Int64.Type}}, {{"BreachMonth", Int64.Type}}, {{"BreachMonthName", type text}},
        {{"BreachQuarter", Int64.Type}}, {{"BreachDay", Int64.Type}}, {{"BreachDayOfWeek", type text}},
        {{"DaysToDatabaseAddition", Int64.Type}}, {{"DaysSinceModification", type number}},
        {{"BreachAgeYears", Int64.Type}}, {{"AffectedAccountsLog", type number}},
        {{"ImpactLevel", type text}}, {{"VerificationStatus", type text}},
        {{"SensitivityStatus", type text}}, {{"MalwareStatus", type text}},
        {{"DataClassCount", Int64.Type}}
    }})
in
    #"Changed Type" """

    m_query_classes = f"""let
    Source = Csv.Document(File.Contents("{CLASSES_CSV}"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Rfc1208]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{
        {{"BreachName", type text}}, {{"Title", type text}}, {{"DataClass", type text}},
        {{"PwnCount", Int64.Type}}, {{"BreachYear", Int64.Type}}, {{"ImpactLevel", type text}},
        {{"IsVerified", type logical}}, {{"IsSensitive", type logical}}
    }})
in
    #"Changed Type" """

    dax_measures = [
        {"name": "Total Breaches", "expression": "COUNTROWS('CleanedBreachData')", "formatString": "#,0"},
        {"name": "Total Accounts Compromised", "expression": "SUM('CleanedBreachData'[PwnCount])", "formatString": "#,0"},
        {"name": "Average Breach Size", "expression": "AVERAGE('CleanedBreachData'[PwnCount])", "formatString": "#,0"},
        {"name": "Median Breach Size", "expression": "MEDIAN('CleanedBreachData'[PwnCount])", "formatString": "#,0"},
        {"name": "Largest Single Breach", "expression": "MAX('CleanedBreachData'[PwnCount])", "formatString": "#,0"},
        {"name": "Smallest Single Breach", "expression": "MIN('CleanedBreachData'[PwnCount])", "formatString": "#,0"},
        {"name": "StdDev Breach Size", "expression": "STDEV.P('CleanedBreachData'[PwnCount])", "formatString": "#,0"},
        {"name": "Verified Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsVerified] = TRUE())", "formatString": "#,0"},
        {"name": "Unverified Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsVerified] = FALSE())", "formatString": "#,0"},
        {"name": "Sensitive Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsSensitive] = TRUE())", "formatString": "#,0"},
        {"name": "Malware-Associated Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsMalware] = TRUE())", "formatString": "#,0"},
        {"name": "Spam List Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsSpamList] = TRUE())", "formatString": "#,0"},
        {"name": "Fabricated Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[IsFabricated] = TRUE())", "formatString": "#,0"},
        {"name": "Critical Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] = \"Critical\")", "formatString": "#,0"},
        {"name": "High Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] = \"High\")", "formatString": "#,0"},
        {"name": "Medium Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] = \"Medium\")", "formatString": "#,0"},
        {"name": "Low Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] = \"Low\")", "formatString": "#,0"},
        {"name": "Critical & High Breaches", "expression": "CALCULATE(COUNTROWS('CleanedBreachData'), 'CleanedBreachData'[ImpactLevel] IN {\"Critical\", \"High\"})", "formatString": "#,0"},
        {"name": "% Verified Breaches", "expression": "DIVIDE([Verified Breaches], [Total Breaches], 0)", "formatString": "0.0%"},
        {"name": "% Sensitive Breaches", "expression": "DIVIDE([Sensitive Breaches], [Total Breaches], 0)", "formatString": "0.0%"},
        {"name": "Mean Intelligence Latency Days", "expression": "AVERAGE('CleanedBreachData'[DaysToDatabaseAddition])", "formatString": "0.0"},
        {"name": "Median Intelligence Latency Days", "expression": "MEDIAN('CleanedBreachData'[DaysToDatabaseAddition])", "formatString": "0"},
        {"name": "Distinct Data Classes Compromised", "expression": "DISTINCTCOUNT('BreachDataClasses'[DataClass])", "formatString": "#,0"}
    ]

    model_bim = {
        "name": "CyberBreachIntelligenceModel",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "tables": [
                {
                    "name": "CleanedBreachData",
                    "columns": [
                        {"name": "Name", "dataType": "string", "isKey": True},
                        {"name": "Title", "dataType": "string"},
                        {"name": "Domain", "dataType": "string"},
                        {"name": "BreachDate", "dataType": "dateTime", "formatString": "yyyy-MM-dd"},
                        {"name": "AddedDate", "dataType": "dateTime"},
                        {"name": "ModifiedDate", "dataType": "dateTime"},
                        {"name": "PwnCount", "dataType": "int64", "formatString": "#,0"},
                        {"name": "Description", "dataType": "string"},
                        {"name": "LogoPath", "dataType": "string"},
                        {"name": "DataClasses", "dataType": "string"},
                        {"name": "IsVerified", "dataType": "boolean"},
                        {"name": "IsFabricated", "dataType": "boolean"},
                        {"name": "IsSensitive", "dataType": "boolean"},
                        {"name": "IsRetired", "dataType": "boolean"},
                        {"name": "IsSpamList", "dataType": "boolean"},
                        {"name": "IsMalware", "dataType": "boolean"},
                        {"name": "IsSubscriptionFree", "dataType": "boolean"},
                        {"name": "BreachYear", "dataType": "int64"},
                        {"name": "BreachMonth", "dataType": "int64"},
                        {"name": "BreachMonthName", "dataType": "string"},
                        {"name": "BreachQuarter", "dataType": "int64"},
                        {"name": "BreachDay", "dataType": "int64"},
                        {"name": "BreachDayOfWeek", "dataType": "string"},
                        {"name": "DaysToDatabaseAddition", "dataType": "int64"},
                        {"name": "DaysSinceModification", "dataType": "double"},
                        {"name": "BreachAgeYears", "dataType": "int64"},
                        {"name": "AffectedAccountsLog", "dataType": "double"},
                        {"name": "ImpactLevel", "dataType": "string"},
                        {"name": "VerificationStatus", "dataType": "string"},
                        {"name": "SensitivityStatus", "dataType": "string"},
                        {"name": "MalwareStatus", "dataType": "string"},
                        {"name": "DataClassCount", "dataType": "int64"}
                    ],
                    "partitions": [
                        {
                            "name": "CleanedBreachData-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": m_query_breaches.split('\n')
                            }
                        }
                    ],
                    "measures": dax_measures
                },
                {
                    "name": "BreachDataClasses",
                    "columns": [
                        {"name": "BreachName", "dataType": "string"},
                        {"name": "Title", "dataType": "string"},
                        {"name": "DataClass", "dataType": "string"},
                        {"name": "PwnCount", "dataType": "int64"},
                        {"name": "BreachYear", "dataType": "int64"},
                        {"name": "ImpactLevel", "dataType": "string"},
                        {"name": "IsVerified", "dataType": "boolean"},
                        {"name": "IsSensitive", "dataType": "boolean"}
                    ],
                    "partitions": [
                        {
                            "name": "BreachDataClasses-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": m_query_classes.split('\n')
                            }
                        }
                    ]
                }
            ],
            "relationships": [
                {
                    "name": "Rel_Breaches_DataClasses",
                    "fromTable": "BreachDataClasses",
                    "fromColumn": "BreachName",
                    "toTable": "CleanedBreachData",
                    "toColumn": "Name"
                }
            ]
        }
    }
    with open(os.path.join(MODEL_DIR, 'model.bim'), 'w', encoding='utf-8') as f:
        json.dump(model_bim, f, indent=2)

    # 5. Report/definition.pbir
    definition_pbir = {
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../CyberBreach_Intelligence.SemanticModel"
            },
            "byConnection": None
        }
    }
    with open(os.path.join(REPORT_DIR, 'definition.pbir'), 'w', encoding='utf-8') as f:
        json.dump(definition_pbir, f, indent=2)

    # 6. Report/definition/version.json & report.json
    def_dir = os.path.join(REPORT_DIR, 'definition')
    pages_dir = os.path.join(def_dir, 'pages')
    os.makedirs(pages_dir, exist_ok=True)

    with open(os.path.join(def_dir, 'version.json'), 'w', encoding='utf-8') as f:
        json.dump({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"}, f, indent=2)

    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU08",
                "type": "SharedResources"
            }
        }
    }
    with open(os.path.join(def_dir, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(report_json, f, indent=2)

    # 7. Report Pages Setup
    pages_metadata = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": ["Page_Overview", "Page_Intelligence", "Page_Entity", "Page_Explorer"],
        "activePageName": "Page_Overview"
    }
    with open(os.path.join(pages_dir, 'pages.json'), 'w', encoding='utf-8') as f:
        json.dump(pages_metadata, f, indent=2)

    page_configs = [
        {"id": "Page_Overview", "name": "Executive Overview"},
        {"id": "Page_Intelligence", "name": "Breach Intelligence"},
        {"id": "Page_Entity", "name": "Entity Analysis"},
        {"id": "Page_Explorer", "name": "Breach Explorer"}
    ]

    for p in page_configs:
        p_dir = os.path.join(pages_dir, p['id'])
        v_dir = os.path.join(p_dir, 'visuals')
        os.makedirs(v_dir, exist_ok=True)

        page_json = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": p['id'],
            "displayName": p['name'],
            "displayOption": "FitToPage",
            "height": 1080,
            "width": 1920
        }
        with open(os.path.join(p_dir, 'page.json'), 'w', encoding='utf-8') as f:
            json.dump(page_json, f, indent=2)

        # Populate Visuals per page
        if p['id'] == 'Page_Overview':
            # Header
            v_title = create_visual_json("v_header", "textbox", 40, 20, 1840, 70, 0)
            v_title["visual"]["objects"] = {
                "general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "CYBERSECURITY DATA BREACH INTELLIGENCE — EXECUTIVE OVERVIEW", "textStyle": {"fontWeight": "bold", "fontSize": "22pt", "color": "#0F172A"}}]}]}}]
            }
            with open(os.path.join(v_dir, 'v_header.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_title, vf, indent=2)

            # 8 KPI Cards
            kpis = [
                ("kpi_1", "Total Breaches", 40, 105, 210, 100, 1),
                ("kpi_2", "Total Accounts Compromised", 270, 105, 210, 100, 2),
                ("kpi_3", "Average Breach Size", 500, 105, 210, 100, 3),
                ("kpi_4", "Largest Single Breach", 730, 105, 210, 100, 4),
                ("kpi_5", "Verified Breaches", 960, 105, 210, 100, 5),
                ("kpi_6", "Sensitive Breaches", 1190, 105, 210, 100, 6),
                ("kpi_7", "Malware-Associated Breaches", 1420, 105, 210, 100, 7),
                ("kpi_8", "Critical & High Breaches", 1650, 105, 230, 100, 8),
            ]
            for vid, mname, x, y, w, h, t_ord in kpis:
                card_v = create_visual_json(vid, "card", x, y, w, h, t_ord,
                    projections={"Values": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": mname}}, "queryRef": mname}]},
                    title=mname)
                with open(os.path.join(v_dir, f"{vid}.json"), 'w', encoding='utf-8') as vf:
                    json.dump(card_v, vf, indent=2)

            # Annual Frequency (Line/Area)
            v_line = create_visual_json("v_annual_freq", "lineChart", 40, 225, 900, 400, 9,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "BreachYear"}}, "queryRef": "BreachYear"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Breaches"}}, "queryRef": "Total Breaches"}]
                },
                title="Annual Breach Frequency & Progression")
            with open(os.path.join(v_dir, 'v_annual_freq.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_line, vf, indent=2)

            # Accounts Affected by Year (Column)
            v_col = create_visual_json("v_accounts_year", "columnChart", 960, 225, 920, 400, 10,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "BreachYear"}}, "queryRef": "BreachYear"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Accounts Compromised"}}, "queryRef": "Total Accounts Compromised"}]
                },
                title="Total Accounts Compromised by Year")
            with open(os.path.join(v_dir, 'v_accounts_year.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_col, vf, indent=2)

            # Top 10 Largest Breaches (Bar)
            v_top10 = create_visual_json("v_top10_breaches", "barChart", 40, 645, 900, 400, 11,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Title"}}, "queryRef": "Title"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Accounts Compromised"}}, "queryRef": "Total Accounts Compromised"}]
                },
                title="Top 10 Largest Historical Data Breaches")
            with open(os.path.join(v_dir, 'v_top10_breaches.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_top10, vf, indent=2)

            # Impact Level Donut
            v_donut = create_visual_json("v_impact_donut", "pieChart", 960, 645, 450, 400, 12,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "ImpactLevel"}}, "queryRef": "ImpactLevel"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Breaches"}}, "queryRef": "Total Breaches"}]
                },
                title="Impact-Level Severity Distribution")
            with open(os.path.join(v_dir, 'v_impact_donut.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_donut, vf, indent=2)

            # Slicer (ImpactLevel)
            v_slicer = create_visual_json("v_slicer_impact", "slicer", 1430, 645, 450, 400, 13,
                projections={
                    "Values": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "ImpactLevel"}}, "queryRef": "ImpactLevel"}]
                },
                title="Filter by Severity Tier")
            with open(os.path.join(v_dir, 'v_slicer_impact.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_slicer, vf, indent=2)

        elif p['id'] == 'Page_Intelligence':
            # Header
            v_title = create_visual_json("v_header", "textbox", 40, 20, 1840, 70, 0)
            v_title["visual"]["objects"] = {
                "general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "BREACH INTELLIGENCE & THREAT ASSET MODELING", "textStyle": {"fontWeight": "bold", "fontSize": "22pt", "color": "#0F172A"}}]}]}}]
            }
            with open(os.path.join(v_dir, 'v_header.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_title, vf, indent=2)

            # Top 20 DataClasses
            v_classes = create_visual_json("v_dataclasses_bar", "barChart", 40, 110, 1050, 930, 1,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "BreachDataClasses"}}, "Property": "DataClass"}}, "queryRef": "DataClass"}],
                    "Y": [{"field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "BreachDataClasses"}}, "Property": "BreachName"}}, "Function": 0}}, "queryRef": "Count"}]
                },
                title="Top Compromised Information Assets (DataClasses)")
            with open(os.path.join(v_dir, 'v_dataclasses_bar.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_classes, vf, indent=2)

            # Latency Column
            v_lat = create_visual_json("v_latency_hist", "columnChart", 1120, 110, 760, 450, 2,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "DaysToDatabaseAddition"}}, "queryRef": "Days"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Breaches"}}, "queryRef": "Total Breaches"}]
                },
                title="Intelligence Latency (Days to Database Addition)")
            with open(os.path.join(v_dir, 'v_latency_hist.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_lat, vf, indent=2)

            # Security Breakdown
            v_sec = create_visual_json("v_security_flags", "columnChart", 1120, 580, 760, 460, 3,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "VerificationStatus"}}, "queryRef": "Verification"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Breaches"}}, "queryRef": "Total Breaches"}]
                },
                title="Verification & Classification Breakdown")
            with open(os.path.join(v_dir, 'v_security_flags.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_sec, vf, indent=2)

        elif p['id'] == 'Page_Entity':
            v_title = create_visual_json("v_header", "textbox", 40, 20, 1840, 70, 0)
            v_title["visual"]["objects"] = {
                "general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "ENTITY INTELLIGENCE & TARGET RE-OCCURRENCE ANALYSIS", "textStyle": {"fontWeight": "bold", "fontSize": "22pt", "color": "#0F172A"}}]}]}}]
            }
            with open(os.path.join(v_dir, 'v_header.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_title, vf, indent=2)

            # Slicer Entity
            v_slicer = create_visual_json("v_entity_slicer", "slicer", 40, 110, 450, 400, 1,
                projections={
                    "Values": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Title"}}, "queryRef": "Title"}]
                },
                title="Search / Select Organization")
            with open(os.path.join(v_dir, 'v_entity_slicer.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_slicer, vf, indent=2)

            # Repeated Entities Bar
            v_rep = create_visual_json("v_repeated_targets", "barChart", 510, 110, 1370, 400, 2,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Domain"}}, "queryRef": "Domain"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Breaches"}}, "queryRef": "Total Breaches"}]
                },
                title="Recurrent Targets: Organizations with Multiple Distinct Breaches")
            with open(os.path.join(v_dir, 'v_repeated_targets.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_rep, vf, indent=2)

            # Timeline
            v_time = create_visual_json("v_entity_timeline", "lineChart", 40, 530, 1840, 510, 3,
                projections={
                    "Category": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "BreachDate"}}, "queryRef": "BreachDate"}],
                    "Y": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Total Accounts Compromised"}}, "queryRef": "Total Accounts Compromised"}]
                },
                title="Breach Incident Sequence & Accounts Compromised Timeline")
            with open(os.path.join(v_dir, 'v_entity_timeline.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_time, vf, indent=2)

        elif p['id'] == 'Page_Explorer':
            v_title = create_visual_json("v_header", "textbox", 40, 20, 1840, 70, 0)
            v_title["visual"]["objects"] = {
                "general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "SEARCHABLE BREACH INCIDENT CATALOG & EXPLORER", "textStyle": {"fontWeight": "bold", "fontSize": "22pt", "color": "#0F172A"}}]}]}}]
            }
            with open(os.path.join(v_dir, 'v_header.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_title, vf, indent=2)

            # Table visual
            v_tbl = create_visual_json("v_catalog_table", "tableEx", 40, 110, 1840, 930, 1,
                projections={
                    "Values": [
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Name"}}, "queryRef": "Name"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Title"}}, "queryRef": "Title"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "Domain"}}, "queryRef": "Domain"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "BreachDate"}}, "queryRef": "BreachDate"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "PwnCount"}}, "queryRef": "PwnCount"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "ImpactLevel"}}, "queryRef": "ImpactLevel"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "VerificationStatus"}}, "queryRef": "VerificationStatus"},
                        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "CleanedBreachData"}}, "Property": "SensitivityStatus"}}, "queryRef": "SensitivityStatus"}
                    ]
                },
                title="Comprehensive Cybersecurity Breach Catalog")
            with open(os.path.join(v_dir, 'v_catalog_table.json'), 'w', encoding='utf-8') as vf:
                json.dump(v_tbl, vf, indent=2)

    print(f"  [+] Configured rich visual definitions for all 4 pages in {REPORT_DIR}")

    # 8. Create Compiled Power BI Template (.pbit)
    print(f"[*] Packaging compiled Power BI Template: {PBIT_PATH}")
    with zipfile.ZipFile(PBIT_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('Version', "1.32".encode('utf-16-le'))
        
        content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="" />
  <Default Extension="xml" ContentType="" />
  <Override PartName="/Version" ContentType="" />
  <Override PartName="/Settings" ContentType="" />
  <Override PartName="/Metadata" ContentType="" />
  <Override PartName="/DataModelSchema" ContentType="" />
</Types>"""
        z.writestr('[Content_Types].xml', content_types.encode('utf-8'))

        settings_data = {"Version": 4, "ReportSettings": {}, "QueriesSettings": {"TypeDetectionEnabled": True, "RelationshipImportEnabled": True}}
        z.writestr('Settings', json.dumps(settings_data).encode('utf-16-le'))

        metadata_data = {"Version": 5, "AutoCreatedRelationships": [], "CreatedFrom": "PowerBIDesktop"}
        z.writestr('Metadata', json.dumps(metadata_data).encode('utf-16-le'))

        z.writestr('DataModelSchema', json.dumps(model_bim, indent=2).encode('utf-16-le'))

        for root, dirs, files in os.walk(REPORT_DIR):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, REPORT_DIR).replace('\\', '/')
                zip_path = f"Report/{rel_p}"
                z.write(full_p, zip_path)

    print(f"  [+] Successfully compiled {PBIT_PATH} ({os.path.getsize(PBIT_PATH):,} bytes)")

if __name__ == '__main__':
    generate_pbip_solution()
