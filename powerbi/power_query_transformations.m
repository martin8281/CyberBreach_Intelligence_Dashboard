// ==========================================================================
// CYBERBREACH INTEL - POWER QUERY (M) TRANSFORMATION SCRIPTS
// Author: Cybersecurity Analytics & Data Engineering Team
// ==========================================================================

// --------------------------------------------------------------------------
// QUERY 1: CleanedBreachData
// --------------------------------------------------------------------------
let
    // 1. Source CSV file ingestion
    Source = Csv.Document(
        File.Contents("c:\Users\Admin\CHRIST\S3\DAS\DAS Mini project\data\cleaned_breach_data.csv"),
        [Delimiter=",", Columns=32, Encoding=65001, QuoteStyle=QuoteStyle.Rfc1208]
    ),
    
    // 2. Promote first row to headers
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    // 3. Explicit Data Type Declarations
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Name", type text},
        {"Title", type text},
        {"Domain", type text},
        {"BreachDate", type date},
        {"AddedDate", type datetimezone},
        {"ModifiedDate", type datetimezone},
        {"PwnCount", Int64.Type},
        {"Description", type text},
        {"LogoPath", type text},
        {"DataClasses", type text},
        {"IsVerified", type logical},
        {"IsFabricated", type logical},
        {"IsSensitive", type logical},
        {"IsRetired", type logical},
        {"IsSpamList", type logical},
        {"IsMalware", type logical},
        {"IsSubscriptionFree", type logical},
        {"BreachYear", Int64.Type},
        {"BreachMonth", Int64.Type},
        {"BreachMonthName", type text},
        {"BreachQuarter", Int64.Type},
        {"BreachDay", Int64.Type},
        {"BreachDayOfWeek", type text},
        {"DaysToDatabaseAddition", Int64.Type},
        {"DaysSinceModification", type number},
        {"BreachAgeYears", Int64.Type},
        {"AffectedAccountsLog", type number},
        {"ImpactLevel", type text},
        {"VerificationStatus", type text},
        {"SensitivityStatus", type text},
        {"MalwareStatus", type text},
        {"DataClassCount", Int64.Type}
    })
in
    #"Changed Type"


// --------------------------------------------------------------------------
// QUERY 2: BreachDataClasses (Normalized 1:N Relation)
// --------------------------------------------------------------------------
let
    // 1. Source CSV file ingestion
    Source = Csv.Document(
        File.Contents("c:\Users\Admin\CHRIST\S3\DAS\DAS Mini project\data\breach_data_classes.csv"),
        [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Rfc1208]
    ),
    
    // 2. Promote first row to headers
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    // 3. Explicit Data Type Declarations
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"BreachName", type text},
        {"Title", type text},
        {"DataClass", type text},
        {"PwnCount", Int64.Type},
        {"BreachYear", Int64.Type},
        {"ImpactLevel", type text},
        {"IsVerified", type logical},
        {"IsSensitive", type logical}
    })
in
    #"Changed Type"
