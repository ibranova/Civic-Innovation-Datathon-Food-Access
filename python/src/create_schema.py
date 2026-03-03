import pandas as pd
import numpy as np
import requests
import os
import re
import time

##### Let's load the all the raw data. ##### 

prioritization_df = pd.read_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/messy/Neighborhood Prioritization Map 2024.csv') # read the prioritization map dataset
shelter_census_df = pd.read_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/messy/Individual_Census_by_Borough,_Community_District,_and_Facility_Type_20260205.csv') # read the shelter census dataset
nta_df = pd.read_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/messy/2020_Neighborhood_Tabulation_Areas_(NTAs)_20260209.csv') # read the NTA_2020 Neighborhood tabulation areas dataset
efap = pd.read_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/messy/EFAP_pdf_11_4_24.csv')

print("Datasets loaded successfully!")

##### Data Cleaning & Feature Engineering #####

#For the prioritization map dataset, we will:
# 1. Standardize column names to lowercase and replace spaces with underscores.
# 2. Handle missing values by filling them with appropriate values or dropping rows/columns if necessary.
# 3. Convert data types to appropriate formats (e.g., numeric, datetime).
# 4. Create new features if needed (e.g., categorizing neighborhoods based on certain criteria).

# Display basic information about the dataset like shape, columns, data types, missing values, and duplicates
print("\n\n--- Neighborhood Prioritization Dataset ---")
print(f"Shape: {prioritization_df.shape}")
print(f"Columns: {list(prioritization_df.columns)}")
print(f"\nData types:\n{prioritization_df.dtypes}")
print(f"\nMissing values:\n{prioritization_df.isnull().sum()}")
print(f"Duplicate rows: {prioritization_df.duplicated().sum()}")

# Let's rename the columns to all lowercase and replace spaces with underscores for consistency
prioritization_df.columns = prioritization_df.columns.str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_')

# Check the updated column names
print(f"\nUpdated Columns: {list(prioritization_df.columns)}")

# Clean Neighborhood Dataset
prioritization_clean = prioritization_df.copy()

# Clean percentage columns (remove % and convert to float)
def clean_percentage(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        return float(x.replace('%', ''))
    return x

# Apply cleaning function to relevant columns by replacing the original columns with cleaned versions

prioritization_clean['food_insecure_percentage'] = prioritization_clean['food_insecure_percentage'].apply(clean_percentage)
prioritization_clean['unemployment_rate'] = prioritization_clean['unemployment_rate'].apply(clean_percentage)
prioritization_clean['vulnerable_population_percentage'] = prioritization_clean['vulnerable_population_percentage'].apply(clean_percentage)
prioritization_clean['supply_gap'] = prioritization_clean['sg_abv_ca']

# A functtion that extrats the borough from NTA code
def extract_borough(nta):
    if nta.startswith('BX'):
        return 'Bronx'
    elif nta.startswith('BK'):
        return 'Brooklyn'
    elif nta.startswith('MN'):
        return 'Manhattan'
    elif nta.startswith('QN'):
        return 'Queens'
    elif nta.startswith('SI'):
        return 'Staten Island'
    else:
        return 'Unknown'
    

# Apply the function to create a new 'borough' column (Feature Engineering)
prioritization_clean['borough'] = prioritization_clean['nta'].apply(extract_borough)

print(f"\nBorough distribution by Neighborhood:\n{prioritization_clean['borough'].value_counts()}")

# let's rename the 'nta' column to 'nta_id' for clarity and to match the naming convention of the other datasets we will be using for analysis
prioritization_clean['nta_id'] = prioritization_clean['nta']

# Drop the original 'nta' column as we now have 'nta_id'
prioritization_clean.drop(columns=['nta'], inplace=True)

#Let's reorder the columns for better readability
prioritization_clean = prioritization_clean[['nta_id', 'nta_name', 'borough', 'food_insecure_percentage','food_insecure_percentage_rank', 'unemployment_rate', 'unemployment_rate_rank', 'vulnerable_population_percentage', 'vulnerable_population_percentage_rank', 'supply_gap', 'weighted_score', 'latitude_generated', 'latitude_generated']]
prioritization_clean = prioritization_clean[['nta_id', 'weighted_score', 'food_insecure_percentage', 'supply_gap', 'vulnerable_population_percentage']]

''' SHELTER CENSUS DATASET '''
#For the shelter census dataset, we will:
# 1. Standardize column names to lowercase and replace spaces with underscores.
# 2. Handle missing values by filling them with appropriate values.
# 3. Convert data types to appropriate formats (e.g., numeric, datetime).
# 4. Create new features if needed (e.g., categorizing facilities based on certain criteria)

# print the shape, columns, and data types of the shelter census dataset
print("\n\n--- Individual Census Dataset ---")
print(f"  4. Shelter Census by CD: {shelter_census_df.shape[0]} rows, {shelter_census_df.shape[1]} columns")
print(f"Columns: {list(shelter_census_df.columns)}")
print(f"\nData types:\n{shelter_census_df.dtypes}")
print(f"\nMissing values:\n{shelter_census_df.isna().sum()}\n")
print(f"Duplicate rows: {shelter_census_df.duplicated().sum()}")

# Let's rename the columns to all lowercase and replace spaces with underscores for consistency 
shelter_census_df.columns = shelter_census_df.columns.str.lower().str.replace(' ', '_')

# Convert report_date to datetime, coercing errors to NaT
shelter_census_df['report_date'] = pd.to_datetime(shelter_census_df['report_date'], format='%m/%d/%Y', errors='coerce')

# print more details about the shelter census dataset like date range, unique report dates, unique boroughs, and unique community districts per borough
print(f"\nDate Range: {shelter_census_df['report_date'].min()} to {shelter_census_df['report_date'].max()}")
print(f"\nUnique Report Dates: {shelter_census_df['report_date'].nunique()}")
print(f"\nUnique Boroughs: {shelter_census_df['borough'].unique()}")
print(f"\nUnique Community Districts per Borough:")
print(shelter_census_df.groupby('borough')['community_districts'].nunique())

'''There is a big gap in the dates from 2018 to 2019. 
We may need to considere that gap for our ARIMAX time series forescasting model. 
There are 90 months from 2018-07-31 to 2026-01-31 and here we have 88 months, we missing 2. '''

# Let's create a copy of the shelter census dataset to work with for cleaning and feature engineering
shelter_census_clean = shelter_census_df.copy()

# Convert numeric columns to numeric types, coercing errors to NaN
numeric_cols = ['adult_family_commercial_hotel','adult_family_shelter','adult_shelter','adult_shelter_commercial_hotel', 'family_cluster', 
                'family_with_children_commercial_hotel', 'family_with_children_shelter']

for col in numeric_cols:
    # Remove commas and convert to numeric
    shelter_census_clean[col] = pd.to_numeric(
        shelter_census_clean[col].astype(str).str.replace(',', ''), 
        errors='coerce'
    )

shelter_census_clean = shelter_census_clean[['report_date', 'borough','community_districts', 'family_with_children_commercial_hotel', 'family_with_children_shelter', 'family_cluster']]

''' NTA DATASET '''
###### For the NTA dataset, we will:
# 1. Standardize column names to lowercase and replace spaces with underscores.
# 2. Handle missing values by filling them with appropriate values.
# 3. Convert data types to appropriate formats (e.g., numeric, datetime).
# 4. Create new features if needed (e.g., categorizing NTAs based on certain criteria)

# print the shape, columns, and data types of the NTA dataset
print("\n\n--- NTA Dataset ---")
print(f"Shape: {nta_df.shape}")
print(f"Columns: {list(nta_df.columns)}")
print(f"\nData types:\n{nta_df.dtypes}")
print(f"\nMissing values:\n{nta_df.isna().sum()}")
print(f"Duplicate rows: {nta_df.duplicated().sum()}")

# delete white spaces in the column id
nta_df['NTA2020'] = nta_df['NTA2020'].str.strip()

# check if the NTA2020 column has unique values
nta_df['NTA2020'].nunique()

print(nta_df.keys())
print(nta_df['NTA2020'].head())
print(nta_df['BoroCode'].value_counts())

# What are the unique borough code/name pairs in this dataset
nta_df[['BoroCode', 'BoroName']].drop_duplicates().sort_values('BoroCode')

nta_df['CDTA2020'].nunique() # there is 71 unuque community district tabulation areas in this dataset, which matches the number of community districts in NYC (5 boroughs x 12 community districts each + 1 for Staten Island which has only 3)

# What are the unique CDTAcode/cdta name pairs in this dataset
nta_df[['CDTA2020', 'CDTAName']].drop_duplicates().head(10)

type(nta_df['the_geom'].iloc[0])

'''The 'the_geom' column contains geometric data in WKT (Well-Known Text) format, which is a text markup language
for representing vector geometry objects. We will rename this column to 'the_geom_wkt' to make it clear 
that it contains WKT data and to avoid confusion with any other geometric data.'''
nta_df = nta_df.rename(columns={'the_geom': 'the_geom_wkt'})


nta_df = nta_df.rename(columns={'NTA2020': 'nta_id'})

''' Let's create a dimension table for the NTA dataset that includes the NTA ID, NTA Name, CDTA code and name,
 borough code and name, and the geometry in WKT format. This dimension table will be useful
   for joining with other datasets based on the NTA ID.'''
dim_map = nta_df[
    [
        'nta_id',
        'NTAName',
        'CDTA2020',
        'CDTAName',
        'BoroCode',
        'BoroName',
        'the_geom_wkt'
    ]
].copy()

dim_map = dim_map.rename(columns={
    'NTAName': 'nta_name',
    'CDTA2020': 'cdta_id',
    'CDTAName': 'cdta_name',
    'BoroCode': 'boro_code',
    'BoroName': 'boro_name'
})



##### Emergency Food Assistance Program (EFAP) Dataset #####
# For the EFAP dataset, we will:
# 1. Standardize column names to lowercase and replace spaces with underscores.
# 2. Handle missing values by filling them with appropriate values.
# 3. Convert data types to appropriate formats (e.g., numeric, datetime).
# 4. Create new features if needed (e.g., categorizing facilities)

print("\n\n--- EFAP Dataset ---")
print(f"Shape: {efap.shape}")
print(f"Columns: {list(efap.columns)}")
print(f"\nData types:\n{efap.dtypes}")
print(f"\nMissing values:\n{efap.isna().sum()}")
print(f"Duplicate rows: {efap.duplicated().sum()}") 

print(efap['TYPE'].value_counts())
print(efap['PROGRAM'].value_counts())
print(efap['PROGRAM'].value_counts().index.tolist())
print(efap['DISTADD'].value_counts().index.tolist())
# chek zipcodes
print(efap['DISTZIP'].value_counts().index.tolist())
efap['DISTZIP'] = efap['DISTZIP'].astype(str).str.strip()
print(efap[['DISTZIP', 'DISTBORO']].head())


efap['DISTBORO'].value_counts()
boro_map = {
    'BK': 'Brooklyn',
    'QN': 'Queens',
    'BX': 'Bronx',
    'SI': 'Staten Island',
    'NY': 'Manhattan'
}

efap['borough'] = efap['DISTBORO'].map(boro_map)


print(efap['borough'].value_counts())
print(efap['ID'].duplicated().sum())

# Check if the 'ID' column has unique values
print(efap['ID'].is_unique)

# let's validata the type of food assistance programs in the EFAP dataset by checking the unique values in the 'PROGRAM'. 
print(efap['TYPE'].value_counts())

# Based on the unique values in the 'TYPE' column, we can categorize the facilities into two main types: 'Pantry' and 'Kitchen'.
pantry_types = {'FP', 'FPH', 'FPM', 'FPV', 'FPK'}
kitchen_types = {'SK', 'SKM', 'SKK', 'FPK'}

# Create new binary features for pantry access and kitchen access based on the 'TYPE' column
efap['has_pantry_access'] = efap['TYPE'].isin(pantry_types).astype(int)
efap['has_kitchen_access'] = efap['TYPE'].isin(kitchen_types).astype(int)

efap['access_type'] = (
    efap['has_pantry_access'].map({1: 'Pantry', 0: ''}) +
    efap['has_kitchen_access'].map({1: ' + Kitchen', 0: ''})).str.strip(' +')
print(efap['access_type'].value_counts())


# Next steps is asking if food is accessible only on weekdays or also on weekends. 

# normalize days column
efap['DAYS_clean'] = efap['DAYS'].str.upper()

weekday_keywords = ['MON', 'TUE', 'WED', 'THU', 'FRI']
weekend_keywords = ['SAT', 'SUN']

efap['weekday_available'] = efap['DAYS_clean'].str.contains(
    '|'.join(weekday_keywords),regex=True,na=False).astype(int)

efap['weekend_available'] = efap['DAYS_clean'].str.contains(
    '|'.join(weekend_keywords), regex=True, na=False).astype(int)

# sanity check to see if the weekday_available column is created correctly
print(efap[['DAYS', 'weekday_available', 'weekend_available']].head(15))

print(efap[['weekday_available', 'weekend_available']].value_counts())
'''We derived binary indicators for weekday and weekend availability based on the presence of day-of-week labels in reported service schedules.
Given substantial variation in schedule formatting, these indicators capture whether any weekday or weekend access exists rather than modeling hours or frequency.'''


## Next steps is to check use the geographic information in the EFAP dataset to map the facilities to the corresponding NTAs and community districts.
#  We can use the DISTADD and DISTZIP columns to geocode the facilities and then spatially join them with the NTA geometries in the dim_map table we created from the NTA dataset. 
# This will allow us to assign each facility to an NTA and community district, which will be crucial for our analysis of food assistance access across different neighborhoods.

print(efap.keys())
print(efap['DISTADD'].value_counts().index.tolist())

# let's validate DISTADD
efap[efap['DISTADD'].isna() | (efap['DISTADD'].str.strip() == '')]

efap['DISTADD'].str.contains(
    'TBD|VARIES|MULTIPLE|UNKNOWN|SEE',
    regex=True,
    na=False
).value_counts()
print(efap['DISTADD'].str.contains(r'\d', regex=True).value_counts())


# build full address (geocoder-friendly)
efap['full_address'] = (efap['DISTADD'].astype(str).str.strip().str.upper()+ ', NEW YORK, NY ' + efap['DISTZIP'].astype(str).str.strip())

# 2) Quick spot check
efap['full_address'].sample(10, random_state=42)


# rename columns to lowercase and replace spaces with underscores
efap.columns = efap.columns.str.lower().str.replace(' ', '_')

# rename columns for clarity and matching naming conventions for the database schema we will be using for analysis.
efap = efap.rename(columns={
    "id": "efap_id",
    'program': 'program_name'})


efap = efap[['efap_id', 'program_name', 'access_type', 'has_pantry_access', 'has_kitchen_access', 'weekday_available', 'weekend_available']]


#### Exporting Cleaned Datasets #####
# Export the cleaned datasets to CSV files for use in analysis and modeling
prioritization_clean.to_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/cleaned_🧼/prioritization_clean.csv', index=False)
shelter_census_clean.to_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/cleaned_🧼/shelter_census_clean.csv', index=False)
dim_map.to_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/cleaned_🧼/dim_map.csv', index=False)
efap.to_csv('/Users/Marcy_Student/Desktop/Food Insecurity Analysis/datasets/cleaned_🧼/efap_clean.csv', index=False)


