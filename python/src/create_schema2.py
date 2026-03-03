import pandas as pd
import numpy as np
import os
from pathlib import Path
import sqlite3

# -----------------------------
# CONFIGURATION (edit paths if needed)
# -----------------------------
RAW_DATA_PATH = '/mnt/data/EFAP_pdf_11_4_24.csv'  # <-- your uploaded CSV
OUTPUT_DIR = Path('data/processed')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_NAME = 'efap_star_schema.db'  # optional: creates a local sqlite file


# -----------------------------
# Helpers
# -----------------------------

def _choose_columns(df, candidates):
    """Return the first subset of candidates that are all present in df."""
    present = [c for c in candidates if c in df.columns]
    return present


def _find_columns_by_keyword(df, keyword):
    return [c for c in df.columns if keyword.lower() in c.lower()]


# -----------------------------
# Main processing function
# -----------------------------

def process_data_for_star_schema(raw_path):
    # Load the raw data
    try:
        df = pd.read_csv(raw_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Raw data not found at {raw_path}")

    print(f"Loaded raw data with {len(df)} rows and {len(df.columns)} columns.")

    # -------------------------
    # 1) BUILDING DIMENSION
    # Prefer common column names, but fall back to heuristics
    # -------------------------
    building_candidates = [
        ['Borough', 'BBL', 'ZipCode'],
        ['Borough', 'BBL', 'ZIP'],
        ['Borough', 'BBL', 'Zip'],
        ['Borough', 'BBL', 'Zipcode'],
        ['Latitude', 'Longitude', 'Address']
    ]

    building_cols = None
    for cand in building_candidates:
        if all(c in df.columns for c in cand):
            building_cols = cand
            break

    if building_cols is None:
        # fallback: take any location-like columns
        loc_like = _find_columns_by_keyword(df, 'zip') + _find_columns_by_keyword(df, 'addr') + _find_columns_by_keyword(df, 'boro')
        # dedupe while preserving order
        seen = set(); loc_like = [x for x in loc_like if not (x in seen or seen.add(x))]
        building_cols = loc_like[:3] if loc_like else []

    print('Building dimension columns chosen:', building_cols)
    if building_cols:
        dim_building = df[building_cols].dropna(how='all').drop_duplicates().reset_index(drop=True)
        dim_building = dim_building.fillna('')
        dim_building['building_id'] = dim_building.index + 1
    else:
        dim_building = pd.DataFrame(columns=['building_id'])

    # -------------------------
    # 2) VIOLATION TYPE DIMENSION
    # -------------------------
    vt_candidates = ['ViolationClass', 'ViolationDescription', 'ViolationType', 'Violation']
    vt_cols = [c for c in vt_candidates if c in df.columns]
    if not vt_cols:
        # fallback: any columns that contain 'violation' or 'type' in name
        vt_cols = _find_columns_by_keyword(df, 'violation') or _find_columns_by_keyword(df, 'viola')

    print('Violation-type columns chosen:', vt_cols)
    if vt_cols:
        dim_violation_type = df[vt_cols].dropna(how='all').drop_duplicates().reset_index(drop=True)
        dim_violation_type = dim_violation_type.fillna('')
        dim_violation_type['violation_type_id'] = dim_violation_type.index + 1
    else:
        dim_violation_type = pd.DataFrame(columns=['violation_type_id'])

    # -------------------------
    # 3) DATE DIMENSION (generate if date-like columns exist)
    # -------------------------
    date_cols = _find_columns_by_keyword(df, 'date')
    date_cols = date_cols or _find_columns_by_keyword(df, 'day')

    dim_date = pd.DataFrame()
    if date_cols:
        # take the first date-like column to build a date dim
        date_col = date_cols[0]
        print('Using date column for dim_date:', date_col)
        # coerce to datetime
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        unique_dates = df[date_col].dropna().drop_duplicates().reset_index(drop=True)
        dim_date = pd.DataFrame({date_col: unique_dates})
        dim_date['date_id'] = dim_date.index + 1
        dim_date['year'] = dim_date[date_col].dt.year
        dim_date['month'] = dim_date[date_col].dt.month
        dim_date['day'] = dim_date[date_col].dt.day
        dim_date['weekday'] = dim_date[date_col].dt.weekday
    else:
        print('No date-like column found; skipping dim_date creation.')

    # -------------------------
    # 4) MERGE FOREIGN KEYS INTO FACT TABLE
    # -------------------------
    fact_df = df.copy()

    # Merge building FK
    if not dim_building.empty:
        merge_on = [c for c in building_cols if c in fact_df.columns]
        fact_df = fact_df.merge(dim_building, on=merge_on, how='left')
        # drop the original building descriptive columns
        fact_df = fact_df.drop(columns=merge_on)

    # Merge violation-type FK
    if not dim_violation_type.empty:
        merge_on = [c for c in vt_cols if c in fact_df.columns]
        fact_df = fact_df.merge(dim_violation_type, on=merge_on, how='left')
        fact_df = fact_df.drop(columns=merge_on)

    # Merge date FK
    if not dim_date.empty:
        date_col = date_cols[0]
        fact_df = fact_df.merge(dim_date[[date_col, 'date_id']], on=date_col, how='left')
        fact_df = fact_df.drop(columns=[date_col])

    # Choose a fact id
    id_candidates = ['ViolationID', 'id', 'ID', 'RecordID']
    fact_id_col = next((c for c in id_candidates if c in fact_df.columns), None)
    if fact_id_col is None:
        # create an id from the index
        fact_df = fact_df.reset_index().rename(columns={'index': 'fact_row_id'})
        fact_id_col = 'fact_row_id'

    # Example measure: is_open if a status column exists
    status_cols = _find_columns_by_keyword(fact_df, 'status')
    if status_cols:
        status_col = status_cols[0]
        fact_df['is_open'] = np.where(fact_df[status_col].astype(str).str.upper().str.contains('OPEN'), 1, 0)
    else:
        fact_df['is_open'] = np.nan

    # Build final fact table with selected FKs and measure columns
    fk_cols = []
    if 'building_id' in fact_df.columns:
        fk_cols.append('building_id')
    if 'violation_type_id' in fact_df.columns:
        fk_cols.append('violation_type_id')
    if 'date_id' in fact_df.columns:
        fk_cols.append('date_id')

    measure_cols = ['is_open']
    fact_table_cols = [fact_id_col] + fk_cols + measure_cols
    fact_table = fact_df[fact_table_cols]

    # -------------------------
    # 5) SAVE CSVS
    # -------------------------
    fact_out = OUTPUT_DIR / 'fact_table.csv'
    fact_table.to_csv(fact_out, index=False)
    print(f"Saved fact table to {fact_out}")

    if not dim_building.empty:
        dim_building_out = OUTPUT_DIR / 'dim_building.csv'
        dim_building.to_csv(dim_building_out, index=False)
        print(f"Saved dim_building to {dim_building_out}")

    if not dim_violation_type.empty:
        dim_violation_out = OUTPUT_DIR / 'dim_violation_type.csv'
        dim_violation_type.to_csv(dim_violation_out, index=False)
        print(f"Saved dim_violation_type to {dim_violation_out}")

    if not dim_date.empty:
        dim_date_out = OUTPUT_DIR / 'dim_date.csv'
        dim_date.to_csv(dim_date_out, index=False)
        print(f"Saved dim_date to {dim_date_out}")

    # -------------------------
    # 6) OPTIONAL: write to sqlite for quick inspection
    # -------------------------
    try:
        conn = sqlite3.connect(DB_NAME)
        fact_table.to_sql('fact_table', conn, if_exists='replace', index=False)
        if not dim_building.empty:
            dim_building.to_sql('dim_building', conn, if_exists='replace', index=False)
        if not dim_violation_type.empty:
            dim_violation_type.to_sql('dim_violation_type', conn, if_exists='replace', index=False)
        if not dim_date.empty:
            dim_date.to_sql('dim_date', conn, if_exists='replace', index=False)
        conn.close()
        print(f"Wrote tables to sqlite DB: {DB_NAME}")
    except Exception as e:
        print('Could not write to sqlite DB (continuing):', e)

    return fact_table, dim_building, dim_violation_type, dim_date


if __name__ == '__main__':
    fact, dbuild, dvt, ddate = process_data_for_star_schema(RAW_DATA_PATH)
    print('\nProcessing complete.')
