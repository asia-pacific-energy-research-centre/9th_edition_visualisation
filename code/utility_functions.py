

import pandas as pd 
import re
import os
from datetime import datetime
import pickle
import shutil
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

ALL_ECONOMY_IDS = ["01_AUS", "02_BD", "03_CDA", "04_CHL", "05_PRC", "06_HKC", "07_INA", "08_JPN", "09_ROK", "10_MAS", "11_MEX", "12_NZ", "13_PNG", "14_PE", "15_PHL", "16_RUS", "17_SGP", "18_CT", "19_THA", "20_USA", "21_VN"]

AGGREGATE_ECONOMY_MAPPING = {
    '00_APEC': ['01_AUS', '02_BD', '03_CDA', '04_CHL', '05_PRC', '06_HKC', '07_INA', '08_JPN', '09_ROK', '10_MAS', '11_MEX', '12_NZ', '13_PNG', '14_PE', '15_PHL', '16_RUS', '17_SGP', '18_CT', '19_THA', '20_USA', '21_VN'],
    '22_SEA': ['02_BD', '07_INA', '10_MAS', '15_PHL', '17_SGP', '19_THA', '21_VN'],
    '23_NEA': ['06_HKC', '08_JPN', '09_ROK', '18_CT'],
    '23b_ONEA': ['06_HKC', '09_ROK', '18_CT'],
    '24_OAM': ['03_CDA', '04_CHL', '11_MEX', '14_PE'],
    '24b_OOAM': ['04_CHL', '11_MEX', '14_PE'],
    '25_OCE': ['01_AUS', '12_NZ', '13_PNG'],
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

def move_workbooks_to_onedrive(origin_date_id=FILE_DATE_ID, econ_list=ALL_ECONOMY_IDS):
    # clean_onedrive_workbooks_folder(date_ids_to_keep='20241211', specific_files_to_keep=[], econ_list=ALL_ECONOMY_IDS, archive_folder_name="first_iteration")
    # clean_onedrive_workbooks_folder(date_ids_to_keep='20241211', specific_files_to_keep=[], econ_list=AGGREGATE_ECONOMY_MAPPING.keys(), archive_folder_name="first_iteration")
    CURRENT_DATE_ID = datetime.now().strftime("%Y%m%d")
    for economy_id in econ_list:
        source_path = f'C:/Users/finbar.maunsell/github/9th_edition_visualisation/output/output_workbooks/{economy_id}/{economy_id}_charts_{origin_date_id}.xlsx'
        destination_path = f'C:/Users/finbar.maunsell/OneDrive - APERC/outlook 9th/Modelling/Visualisation/{economy_id}/{economy_id}_charts_{CURRENT_DATE_ID}.xlsx'
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Move the file
        shutil.copy(source_path, destination_path)
        print(f"Moved {source_path} to {destination_path}")

def clean_onedrive_workbooks_folder(date_ids_to_keep, specific_files_to_keep, econ_list, archive_folder_name="archive"):
    # clean_onedrive_workbooks_folder(date_ids_to_keep=['20241211'], specific_files_to_keep=[], econ_list=["01_AUS", "02_BD", "03_CDA", "04_CHL", "05_PRC", "06_HKC", "07_INA", "08_JPN", "09_ROK", "10_MAS", "11_MEX", "12_NZ", "13_PNG", "14_PE", "15_PHL", "16_RUS", "17_SGP", "18_CT", "19_THA", "20_USA", "21_VN"], archive_folder_name="first_iteration")
    # clean_onedrive_workbooks_folder(date_ids_to_keep=['20241211'], specific_files_to_keep=[], econ_list=AGGREGATE_ECONOMY_MAPPING.keys(), archive_folder_name="first_iteration")
    for economy_id in econ_list:
        base_path = f'C:/Users/finbar.maunsell/OneDrive - APERC/outlook 9th/Modelling/Visualisation/{economy_id}/'
        archive_path = os.path.join(base_path, archive_folder_name)
        
        # Create archive directory if it doesn't exist
        os.makedirs(archive_path, exist_ok=True)
        
        for file_name in os.listdir(base_path):
            file_path = os.path.join(base_path, file_name)
            
            # Check if it's a file and not a directory
            if os.path.isfile(file_path):
                # Check if the file does not contain any of the date_ids_to_keep and is not in specific_files_to_keep
                if all(date_id not in file_name for date_id in date_ids_to_keep) and file_name not in specific_files_to_keep:
                    shutil.move(file_path, os.path.join(archive_path, file_name))
                    print(f"Moved {file_path} to {archive_path}")