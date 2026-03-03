-- STAR SCHEMA: NYC Food & Shelter Access Database
-- 1. DIMENSION TABLES

-- dim_date: Date dimension with year, month, and YearMonth
CREATE TABLE dim_date (
    date_id     INT         PRIMARY KEY,
    year        INT         NOT NULL,
    month       INT,
    YearMonth   TEXT
);

-- dim_map: where shelters are located (NTA-level)
CREATE TABLE dim_map (
    nta_id      TEXT        PRIMARY KEY,
    nta_name    TEXT        NOT NULL,
    cdta_id     TEXT,                       -- attribute (not PK)
    cdta_name   TEXT,
    boro_code   INT,
    boro_name   TEXT,
    the_geom_wkt MULTIPOLYGON
);


-- dim_cdta: bridge to connect shelter facts to dim_map — extracted from dim_map to allow clean FK from shelter fact
CREATE TABLE dim_cdta (
    cdta_id     TEXT        PRIMARY KEY,
    cdta_name   TEXT,
    boro_code   INT,
    boro_name   TEXT
);

-- dim_program_schedule: EFAP program details on food programs
CREATE TABLE dim_program_schedule (
    efap_id             INT         PRIMARY KEY,
    program_name        VARCHAR     NOT NULL,
    access_type         VARCHAR,
    has_pantry_access   INT,
    has_kitchen_access  INT,
    weekend_available   INT,
    weekday_available   INT
);

-- 2. BRIDGE TABLE (many-to-many relationship between dim_program & dim_map)
CREATE TABLE bridge_efap_site_nta (
    efap_id     INT         NOT NULL,
    nta_id      TEXT        NOT NULL, 
    PRIMARY KEY (efap_id, nta_id),
    FOREIGN KEY (efap_id) REFERENCES dim_program_schedule (efap_id),
    FOREIGN KEY (nta_id)  REFERENCES dim_map (nta_id)
);


-- 3. FACT TABLES

-- fact_neighborhood_prioritization
CREATE TABLE fact_neighborhood_prioritization (
    nta_id                      TEXT        NOT NULL,
    date_id                     INT         NOT NULL,
    weighted_score              DECIMAL,
    food_insecure_percentage    DECIMAL,
    supply_gap                  DECIMAL,
    vulnerable_pop_percentage   DECIMAL,
    is_high_priority            INT,
    UNIQUE (nta_id, date_id),
    FOREIGN KEY (nta_id)  REFERENCES dim_map (nta_id), -- nta_id is FK only becauce it reference dimensions, not identify the fact
    FOREIGN KEY (date_id) REFERENCES dim_date (date_id) )


-- fact_food_site_coverage
CREATE TABLE fact_food_site_coverage (
    nta_id              TEXT        NOT NULL,
    date_id             INT         NOT NULL,
    pantry_site_count   INT,
    kitchen_site_count  INT,
    total_sites         INT,
    weekend_site_count  INT,
    weekday_site_count  INT,
    UNIQUE (nta_id, date_id),
    FOREIGN KEY (nta_id)  REFERENCES dim_map (nta_id),
    FOREIGN KEY (date_id) REFERENCES dim_date (date_id) -- nta_id and date_id are FKs only — they reference dimensions, not identify the fact
);


-- fact_agg_shelter_cdta_year
CREATE TABLE fact_agg_shelter_cdta_year (
    cdta_id                         TEXT        NOT NULL,
    date_id                         INT         NOT NULL,
    boro                            TEXT,
    family_with_children_commercial_hotel   INT,
    family_with_children_count      INT,
    family_cluster                  INT,
    UNIQUE (cdta_id, date_id),
    FOREIGN KEY (cdta_id) REFERENCES dim_cdta (cdta_id), -- cdta_id is FK only, it reference the dimension table (Cdta), not identify the fact itself
    FOREIGN KEY (date_id) REFERENCES dim_date (date_id) -- date_id is FK only because it references the dimension date, not identify the fact it self
);
