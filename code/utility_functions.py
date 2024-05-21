

import pandas as pd 
import re
import os
from datetime import datetime


ECONOMY_ID = '15_PHL'#08_JPN

#######################################################
#CONFIG PREPARATION
#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')

# FILE_DATE_ID = '20231110'
total_plotting_names=['Total', 'TPES', 'Total primary energy supply','TFEC', 'TFC', 'Total_industry', 'Total_transport']
MIN_YEAR = 2000

EXPECTED_COLS = ['source', 'table_number', 'chart_type','plotting_name', 'plotting_name_column','aggregate_name', 'aggregate_name_column', 'scenario', 'unit', 'table_id', 'dimensions', 'chart_title', 'year', 'value','sheet_name']

EBT_EARLIEST_YEAR = 1980
OUTLOOK_BASE_YEAR = 2021
OUTLOOK_LAST_YEAR = 2060

def find_most_recent_file_date_id(directory_path):
    """Find the most recent file in a directory based on the date ID in the filename."""
    # List all files in the directory
    files = os.listdir(directory_path)

    # Initialize variables to keep track of the most recent file and date
    most_recent_date = datetime.min
    most_recent_file = None

    # Define a regex pattern for the date ID (format YYYYMMDD)
    date_pattern = re.compile(r'(\d{8})')
    
    # Loop through the files to find the most recent one
    for file in files:
        # Use regex search to find the date ID in the filename
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
    return most_recent_file