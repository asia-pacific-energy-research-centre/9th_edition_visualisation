

import pandas as pd 
import re
import os
from datetime import datetime
import pickle
STRICT_DATA_CHECKING = False

# ECONOMY_ID = '22_SEA'#'00_APEC'#08_JPN#tremoved this because its just confusing. might as well set it in the script

#######################################################
#CONFIG PREPARATION
#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')

FILE_DATE_ID = '20241112'
total_plotting_names=['Total', 'TPES', 'Total primary energy supply','TFEC', 'TFC', 'Total_industry', 'Total_transport', 'Total_fuels', 'Total combustion emissions']
MIN_YEAR = 2000

EXPECTED_COLS = ['source', 'table_number', 'chart_type','plotting_name', 'plotting_name_column','aggregate_name', 'aggregate_name_column', 'scenario', 'unit', 'table_id', 'dimensions', 'chart_title', 'year', 'value','sheet_name']

SCENARIOS_list = ['reference', 'target']

ALL_ECONOMY_IDS = ["01_AUS", "02_BD", "03_CDA", "04_CHL", "05_PRC", "06_HKC", "07_INA", "08_JPN", "09_ROK", "10_MAS", "11_MEX", "12_NZ", "13_PNG", "14_PE", "15_PHL", "16_RUS", "17_SGP", "18_CT", "19_THA", "20_USA", "21_VN"]#,'00_APEC', '23b_ONEA', '22_SEA', '23_NEA', '24_OAM', '25_OCE']
AGGREGATE_ECONOMY_MAPPING = {
    '00_APEC': ['01_AUS', '02_BD', '03_CDA', '04_CHL', '05_PRC', '06_HKC', '07_INA', '08_JPN', '09_ROK', '10_MAS', '11_MEX', '12_NZ', '13_PNG', '14_PE', '15_PHL', '16_RUS', '17_SGP', '18_CT', '19_THA', '20_USA', '21_VN'],
    '22_SEA': ['02_BD', '07_INA', '10_MAS', '15_PHL', '17_SGP', '19_THA', '21_VN'],
    '23_NEA': ['05_PRC', '06_HKC', '08_JPN', '09_ROK', '18_CT'],
    '23b_ONEA': ['01_AUS', '05_PRC', '06_HKC', '08_JPN', '09_ROK', '12_NZ', '13_PNG', '18_CT'],
    '24_OAM': ['01_AUS', '03_CDA', '04_CHL', '11_MEX', '12_NZ', '13_PNG', '14_PE', '20_USA'],
    '25_OCE': ['01_AUS', '02_BD', '05_PRC', '06_HKC', '07_INA', '08_JPN', '09_ROK', '10_MAS', '12_NZ', '13_PNG', '15_PHL', '17_SGP', '18_CT', '19_THA', '21_VN'],
    '26_NA': ['03_CDA', '20_USA'],
}

EBT_EARLIEST_YEAR = 1980
OUTLOOK_BASE_YEAR = 2022
OUTLOOK_LAST_YEAR = 2060

PROJ_YEARS = list(range(OUTLOOK_BASE_YEAR+1, OUTLOOK_LAST_YEAR+1, 1))
HIST_YEARS = list(range(EBT_EARLIEST_YEAR, OUTLOOK_BASE_YEAR+1, 1))
HIST_YEARS_str = [str(year) for year in HIST_YEARS]
PROJ_YEARS_str = [str(year) for year in PROJ_YEARS]

def find_most_recent_file_date_id(directory_path, filename_part = None,RETURN_DATE_ID = False):
    """Find the most recent file in a directory based on the date ID in the filename."""
    # List all files in the directory
    files = os.listdir(directory_path)

    # Initialize variables to keep track of the most recent file and date
    most_recent_date = datetime.min
    most_recent_file = None
    date_id = None
    # Define a regex pattern for the date ID (format YYYYMMDD)
    date_pattern = re.compile(r'(\d{8})')
    
    # Loop through the files to find the most recent one
    for file in files:
        if filename_part is not None:
            if filename_part not in file:
                continue
        # Use regex search to find the date ID in the filename
        if os.path.isdir(os.path.join(directory_path, file)):
            continue
        match = date_pattern.search(file)
        if match:
            date_id = match.group(1)
            # Parse the date ID into a datetime object
            try:
                file_date = datetime.strptime(date_id, '%Y%m%d')
                # If this file's date is more recent, update the most recent variables
                if file_date > most_recent_date:
                    most_recent_date = file_date
                    most_recent_file = file
            except ValueError:
                # If the date ID is not in the expected format, skip this file
                continue

    # Output the most recent file
    if most_recent_file:
        print(f"The most recent file is: {most_recent_file} with the date ID {most_recent_date.strftime('%Y%m%d')}")
    else:
        print("No files found with a valid date ID.")
    if RETURN_DATE_ID:
        return most_recent_file, date_id
    else:
        return most_recent_file
    

def save_checkpoint(df, name, folder='../intermediate_data/checkpoints/'):
    """
    Save a DataFrame or data object as a checkpoint using pickle.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
    with open(filepath, 'wb') as f:
        try:
            pickle.dump(df, f)
            print(f"Checkpoint saved: {filepath}")
        except TypeError as e:
            print(f"Failed to save checkpoint {name}: {e}")

def load_checkpoint(name, folder='../intermediate_data/checkpoints/'):
    """
    Load a checkpoint from a pickle file.
    """
    checkpoints = [f for f in os.listdir(folder) if name in f and f.endswith('.pkl')]
    if not checkpoints:
        raise FileNotFoundError(f"No checkpoint found for {name}")
    checkpoints.sort()  # Sort by timestamp
    filepath = os.path.join(folder, checkpoints[-1])  # Load the latest checkpoint
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    print(f"Checkpoint loaded: {filepath}")
    return data

def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)
