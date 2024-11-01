#Functions used in 1_map_9th_data_to_plotting_template.py. They are to do with mapping but include some adjacent tasks such as data checking, plotting and formatting.
#%%
import pickle
import pandas as pd
import numpy as np
import os
import collections
import re
from datetime import datetime
from utility_functions import *
STRICT_DATA_CHECKING = False


def find_most_recent_file_date_id(files):
    """Find the most recent file in a directory based on the date ID in the filename."""

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

def find_and_load_latest_data_for_all_sources(ECONOMY_ID, sources): 
    # Initialize variables
    all_file_paths = []
    folder =f'../input_data/{ECONOMY_ID}/'
    all_model_df_wides_dict = {}
    # Fetch file paths based on the configuration

    for root, dirs, files in os.walk(folder):
        all_file_paths.extend([os.path.join(root, file) for file in os.listdir(root) if os.path.isfile(os.path.join(root, file))])

    # Check if files are found
    if not all_file_paths:
        raise Exception(f"No file found for {folder}")

    #find latest files for each source:
    all_files_with_source = []
    for source in sources:
        all_file_paths_source = [file_path for file_path in all_file_paths if source in os.path.basename(file_path)]
        all_files_with_source = all_files_with_source + all_file_paths_source
        if len(all_file_paths_source) == 0:
            print(f'No file found for {source}')
        #find file with latest file date id using find_most_recent_file_date_id(files)
        file_path = find_most_recent_file_date_id(all_file_paths_source)
        all_model_df_wides_dict[source] = [file_path]
        if file_path is None:
            print(f'No latest date id was idenitfied for {source} files')
        
    # Check if there are any files_missing_source
    files_missing_source = [file_path for file_path in all_file_paths if file_path not in all_files_with_source]
    if len(files_missing_source) > 0:
        print(f'The following files were not identified as an energy, capacity or emissions file: {files_missing_source}')
    
    def load_data_to_df(file_path):
        if file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            raise Exception(f"Unsupported file format for {file_path}")

    # Load data into DataFrames and
    for source in all_model_df_wides_dict.keys():
        file_path = all_model_df_wides_dict[source][0]
        all_model_df_wides_dict[source].append(load_data_to_df(file_path))
        
    return all_model_df_wides_dict


def format_plotting_mappings(plotting_mappings_df, columns, plotting_name_column, strict_data_checking=False):
    # Initialize the new plotting mappings data frame with the necessary columns
    new_plotting_mappings = pd.DataFrame(columns=['plotting_name','plotting_name_column', 'reference_name', 'reference_name_column'])
    #to handle the extra detail of the sheet column, we need to add it to the new_plotting_mappings. Worried that this is a bit complicated and could be done better
    if 'sheet' in columns:
        new_plotting_mappings = pd.DataFrame(columns=['plotting_name','plotting_name_column', 'reference_name', 'reference_name_column', 'sheet'])

    # Loop through each column in the specified order
    original_plotting_mappings_df = plotting_mappings_df.copy()
    previous_col_valid_rows = 0
    for col in columns:
        #########CHECK##########
        #first check that the number of valid rows is more than the previous number of valid rows, otherwise we are not going in order of least to most specific columns:
        valid_rows_test = original_plotting_mappings_df[original_plotting_mappings_df[col].notna()]
        if len(valid_rows_test) < previous_col_valid_rows:
            raise ValueError('The number of valid rows for the column {} is less than or equal to the previous column. This means that the columns are not in order of least to most specific. You will have to fix the all_plotting_mapping_dicts for this plotting_mappings_df'.format(col))
        else:
            previous_col_valid_rows = len(valid_rows_test)
        #########CHECK OVER##########
        # Filter out rows where the column value is not NA
        valid_rows = plotting_mappings_df[plotting_mappings_df[col].notna()]
        # Create a new data frame from the non-NA rows
        new_rows = pd.DataFrame({
            'plotting_name': valid_rows[plotting_name_column],
            'plotting_name_column': plotting_name_column,
            'reference_name': valid_rows[col],
            'reference_name_column': col,
            'source': valid_rows['source']
        })#plotting_name ?
        if 'sheet' in columns:
            new_rows['sheet'] = valid_rows['sheet']

        # Append the new rows to the new plotting mappings data frame
        new_plotting_mappings = pd.concat([new_plotting_mappings, new_rows], ignore_index=True)

        # Remove the processed rows to avoid double counting
        plotting_mappings_df = plotting_mappings_df[plotting_mappings_df[col].isna()]
    
    # Check for NAs in the entire data frame
    if new_plotting_mappings.isna().sum().sum() > 0 and strict_data_checking:
        raise ValueError('There are still some NAs in the new_plotting_mappings')

    return new_plotting_mappings

def format_charts_mapping(charts_mapping, source_and_aggregate_name_column_to_plotting_name_column_mapping_dict):
    # Drop the first row which is a header row
    charts_mapping = charts_mapping.iloc[1:]

    # Define key columns
    key_cols = ['source', 'sheet_name', 'table_number', 'chart_type', 'chart_title']
    
    # Assuming 'aggregate_name_column' holds the column names to aggregate by
    aggregate_name_columns = charts_mapping['aggregate_name_column'].unique()

    # Prepare the final DataFrame
    new_charts_mapping = pd.DataFrame()

    for aggregate_name_column in aggregate_name_columns:
        # Get the subset of the DataFrame for the current aggregate column name
        subset = charts_mapping[charts_mapping['aggregate_name_column'] == aggregate_name_column]

        # Get unique values for the aggregate column under the current aggregate column name
        unique_aggregates = subset['aggregate_name'].unique()

        for aggregate in unique_aggregates:
            # Filter the DataFrame for the current aggregate
            aggregated = subset[subset['aggregate_name'] == aggregate]

            # # Determine the plotting columns (group 3 columns)
            # group_3_cols = [x for x in charts_mapping.columns if x not in key_cols + ['aggregate_name_column', 'aggregate_name']]

            # Melt the dataframe on group 3 columns
            melted = pd.melt(aggregated, id_vars=key_cols + ['aggregate_name_column', 'aggregate_name'], value_name='plotting_name', var_name='digits')

            # Drop the 'digits' column and any NAs in the 'plotting_name' column
            melted.drop(columns=['digits'], inplace=True)
            melted.dropna(subset=['plotting_name'], inplace=True)

            # Add a column to identify the aggregate column
            melted['aggregate_name_column'] = aggregate_name_column
            melted['aggregate_name'] = aggregate

            # Append to the final DataFrame
            new_charts_mapping = pd.concat([new_charts_mapping, melted], ignore_index=True)
            
    #set the plotting_name_column based on what the aggregate_name_column is and source is:   
    for source in new_charts_mapping['source'].unique():
        #if the mapping doesent work then it should be an error from user input, so raise an error
        new_charts_mapping.loc[new_charts_mapping['source'] == source, 'plotting_name_column'] = new_charts_mapping['aggregate_name_column'].map(source_and_aggregate_name_column_to_plotting_name_column_mapping_dict[source])
        if new_charts_mapping.loc[(new_charts_mapping['source'] == source) &(new_charts_mapping.plotting_name_column.isna())].shape[0] > 0:
            raise ValueError('There is a source in the new_charts_mapping that does not have a plotting_name_column. This is likely because the source_and_aggregate_name_column_to_plotting_name_column_mapping_dict is missing a source or aggregate_name_column. Otherwise you might have entered data wrong in the master_configs source or aggregate_name_column. Please check the source_and_aggregate_name_column_to_plotting_name_column_mapping_dict for the source: ', source)
    
    # Create a unique identifier for each source, sheet and table number
    new_charts_mapping['table_id'] = new_charts_mapping['source'] + '_' + new_charts_mapping['sheet_name'] + '_' + new_charts_mapping['table_number'].astype(str)

    return new_charts_mapping

def save_plotting_names_order(charts_mapping,FILE_DATE_ID):
    key_cols = ['source', 'sheet_name', 'table_number', 'chart_type', 'chart_title']
    group_2_cols = ['aggregate_name_column', 'aggregate_name']
    group_3_cols = [x for x in charts_mapping.columns.tolist() if x not in key_cols + group_2_cols]
    #create table_id col
    charts_mapping['table_id'] = charts_mapping['source'] + '_' + charts_mapping['sheet_name'] + '_' + charts_mapping['table_number'].astype(str)

    charts_mapping_pivot = charts_mapping[['table_id'] + group_3_cols].drop_duplicates()
    #set index to 'table_id'
    charts_mapping_pivot = charts_mapping_pivot.set_index('table_id')
    # #drop nas
    # charts_mapping_pivot = charts_mapping_pivot.dropna()
    #put it into a dictionary such that every key is  the 'table_id', and the value is a list of the group_3_cols in order, excluding nas
    plotting_names_order = {}
    #check there are no dsuplicates in charts_mapping_pivot.index.tolist(). this is where we;d have two cahrts of same name and it will cause an error
    if len(charts_mapping_pivot.index.tolist()) != len(set(charts_mapping_pivot.index.tolist())): 
        raise ValueError('There are duplicated in the table_id column. You probably have two tables of the same table number for the same sheet: ', [item for item, count in collections.Counter(charts_mapping_pivot.index.tolist()).items() if count > 1])
    for table_id in charts_mapping_pivot.index.tolist():
        plotting_names_order[table_id] = [x for x in charts_mapping_pivot.loc[table_id].tolist() if str(x) != 'nan']
            
    # Save dictionary into file
    with open(f'../intermediate_data/config/plotting_names_order_{FILE_DATE_ID}.pkl', 'wb') as handle:
        pickle.dump(plotting_names_order, handle, protocol=pickle.HIGHEST_PROTOCOL)

def test_charts_mapping(charts_mapping):
    #things to test:
    #where there is a bar chart, it is the only chart for that table number, else throw error (this is because bar charts are split by 10 year intervals so need their own table.)
    bar_charts = charts_mapping[charts_mapping['chart_type'] == 'bar']
    #chekc if the table id is anywher else in the df
    non_bar_charts = charts_mapping[charts_mapping['chart_type'] != 'bar']
    errors = bar_charts[bar_charts['table_id'].isin(non_bar_charts['table_id'].unique().tolist())]
    if len(errors) > 0:
        print(errors)
        raise Exception('There is a bar chart that is not the only chart for that table id. This shouldnt happen because bar charts are split by X year intervals so need their own table.')

def test_plotting_names_match_charts_mapping(plotting_names,new_charts_mapping):
    #double check teh unique plotting anmes in both new_charts_mapping and plotting_df are exactly the same otherwise, if there are any plotting names in new_charts_mapping that are not in plotting_df then we will have a problem, and if there are any plotting names in plotting_df that are not in new_charts_mapping then we should let the user know in case they want to remove them from the plotting_df
    new_charts_mapping_names = set(new_charts_mapping.plotting_name.unique())
    if len(plotting_names) > len(new_charts_mapping_names):
        different_names = plotting_names - new_charts_mapping_names
        print('there are plotting names in the mappings (e.g. fuels, sectors, capacity, emissions mappings) that are not in new_charts_mapping. These are:\n ', different_names, '\n This is not an immediate problem, but you may want to remove them from the plotting_df if its getting cluttered.')
    elif len(plotting_names) < len(new_charts_mapping_names):
        different_names = new_charts_mapping_names - plotting_names
        raise ValueError('there are plotting names in new_charts_mapping that are not in the mappings (e.g. fuels, sectors, capacity, emissions mappings). These are: \n', different_names)
    else:
        pass
        
def test_plotting_names_match_colors_df(plotting_names,colors_df):
    #also check that colors_df.Plotting_name is the same as plotting_df.plotting_name
    colors_plotting_names = set(colors_df.plotting_name.unique())
    if len(plotting_names) > len(colors_plotting_names):
        different_names = plotting_names - colors_plotting_names
        raise ValueError('there are plotting names in plotting_df that are not in colors_df. These are:\n ', different_names)
    elif len(plotting_names) < len(colors_plotting_names):
        different_names = colors_plotting_names - plotting_names
        print('there are plotting names in colors_df that are not in plotting_df. These are:\n ', different_names)
    else:
        pass 
        
def check_data_matches_expectations(model_df_wide_economy, model_variables,RAISE_ERROR=True):
    #drop first 2 rows (includes the columns row) and check the next row is a set of columns that match the object columns in the Data sheet

    #we first need to check that the columns in the Variables sheet match the columns in the Data sheet
    object_columns = model_df_wide_economy.select_dtypes(include=['object']).columns.to_list()
    #drop source and sheet cols if they exist
    if 'source' in object_columns:
        object_columns.remove('source')
    if 'sheet' in object_columns:
        object_columns.remove('sheet')    
    #check the difference between the columns in the Variables sheet and the columns in the Data sheet
    diff = set(object_columns) - set(model_variables.columns.to_list())
    if len(list(diff)) > 0:
        print('The following columns between the Variables sheet and the Data are different: ', diff)
        breakpoint()
        raise Exception(f'The following columns in the Variables sheet do not match the columns in the Data sheet: {diff}')

    #Now check that the unique variables in the columns in the Variables sheet match the unique variables in the columns in the Data sheet
    for col in object_columns:
        unique_variables = model_variables[col].dropna().unique()
        unique_variables.sort()
        unique_variables_data = model_df_wide_economy[col].dropna().unique()
        unique_variables_data.sort()
        diff = np.setdiff1d(unique_variables, unique_variables_data)
        data_sheet_missing_list = []
        variables_missing_list = []
        if len(diff) > 0:
            #determine whether its missing from the Variables sheet or the Data sheet
            for variable in diff:
                #skip the economy column
                if col == 'economy':
                    continue
                elif variable in unique_variables:
                    if RAISE_ERROR:
                        raise Exception('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
                    # print('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
                    data_sheet_missing_list.append(variable)
                else:
                    if RAISE_ERROR:
                        raise Exception('The variable {} in the column {} is missing from the Variables sheet'.format(variable, col))
                    # print('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
                    variables_missing_list.append(variable)
            if len(data_sheet_missing_list) > 0:
                print('In the column {}, these variables are missing from the Data sheet {}'.format(col, data_sheet_missing_list))
            if len(variables_missing_list) > 0:
                print('In the column {}, these variables are missing from the Variables sheet {}'.format(col, variables_missing_list))


def check_missing_plotting_name_values_when_merging_mappings_to_modelled_data(columns, plotting_name_column, new_plotting_mappings, plotting_mappings, model_df_tall, RAISE_ERROR):
    new_df = model_df_tall[['plotting_name']+columns].drop_duplicates().replace('x', np.nan)
    plotting_name_column = new_plotting_mappings['plotting_name_column'].unique()[0]
    mapping = plotting_mappings[[plotting_name_column]+columns].drop_duplicates()
    
    #before the merge make sure all the cols plotting_name_column]+columns and ['plotting_name']+columns are object cols
    new_df['plotting_name'] = new_df['plotting_name'].astype(str)
    mapping[plotting_name_column] = mapping[plotting_name_column].astype(str)
    for col in columns:
        new_df[col] = new_df[col].astype(str)
        mapping[col] = mapping[col].astype(str)
        
    # Merge the dataframes and add an indicator column
    merged_df = pd.merge(new_df, mapping, left_on=['plotting_name']+columns, right_on=[plotting_name_column]+columns, how='outer', indicator=True)
    # Find rows that are only in mapping
    missing_in_new_model = merged_df[merged_df['_merge'] == 'right_only']
    if len(missing_in_new_model) > 0:
        if RAISE_ERROR:
            raise Exception('There are plotting_name values for {} that may have been lost in the merge. They are probably just missing from the input data. This may or may not be important depending on the rows. These are: {}'.format(plotting_name_column, missing_in_new_model))
        print('There are plotting_name values for {} that may have been lost in the merge. They are probably just missing from the input data. This may or may not be important depending on the rows. These are: {}'.format(plotting_name_column, missing_in_new_model))#This could be because they dont match any original categories, or *unlikely* they arent used by any of the sectors referenced in sectors plotting
    
def merge_sector_mappings(model_df_tall, new_sector_plotting_mappings, sector_plotting_mappings, RAISE_ERROR=True):
    new_model_df_tall = model_df_tall.copy()
    new_model_df_tall = new_model_df_tall[0:0]  # Empty it
    for unique_col in new_sector_plotting_mappings['reference_name_column'].unique():#i think reference column will always be 'sectors_plotting' . maybve can remove this
        columns_data = new_sector_plotting_mappings[new_sector_plotting_mappings['reference_name_column'] == unique_col]
        columns_data = columns_data[['plotting_name', 'reference_name']]
        columns_data = model_df_tall.merge(columns_data, how='inner', left_on=unique_col, right_on='reference_name')
        new_model_df_tall = pd.concat([new_model_df_tall, columns_data])
    
    check_missing_plotting_name_values_when_merging_mappings_to_modelled_data([ 'sectors', 'sub1sectors', 'sub2sectors'], new_sector_plotting_mappings['plotting_name_column'].unique()[0], new_sector_plotting_mappings, sector_plotting_mappings, new_model_df_tall, RAISE_ERROR)

    # Drop unnecessary columns
    new_model_df_tall = new_model_df_tall.drop(columns=['sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'reference_name'])
    
    #? rename plotting_name to sectors_plotting_name, just for clarity when we merge the fuel mappings. 
    new_model_df_tall = new_model_df_tall.rename(columns={'plotting_name': 'sectors_plotting'})
    return new_model_df_tall


def merge_fuel_mappings(model_df_tall_sectors, new_fuel_plotting_mappings,fuel_plotting_mappings, RAISE_ERROR=True):
    #using the plotting mappings which were created in the format_plotting_mappings function, we need to merge these onto the model_df_tall using the reference_name_column and reference_fuel columns, where the reference column specifies the column to find the reference fuel in the model_df_tall. This is the same as the merge_sector_mappings function, But importantly, the result from merge_sector_mappings is used instead of the model_df_tall, and so the output of this will contain the sectors_plotting column
    #now we join on the fuels mappigns:
    new_new_model_df_tall = model_df_tall_sectors.copy()
    #empty it
    new_new_model_df_tall = new_new_model_df_tall[0:0]
    #so join the new_fuel_plotting_mappings to the model_df_tall
    for unique_col in new_fuel_plotting_mappings.reference_name_column.unique():
        columns_data = new_fuel_plotting_mappings[new_fuel_plotting_mappings.reference_name_column == unique_col][['plotting_name', 'reference_name']]
        
        #filter for the unique col and then join on the unique col to the model_df_tall
        columns_data = model_df_tall_sectors.merge(columns_data, how='inner', left_on=unique_col, right_on='reference_name')
        #concat to the new_model_df_tall
        new_new_model_df_tall = pd.concat([new_new_model_df_tall, columns_data])
    #and to be more precise, check the uniqe rows for the columns [[plotting_name	fuels	subfuels]] in the fuels_mappings are all in the new_new_model_df_tall
    check_missing_plotting_name_values_when_merging_mappings_to_modelled_data(['fuels', 'subfuels'], new_fuel_plotting_mappings['plotting_name_column'].unique()[0], new_fuel_plotting_mappings, fuel_plotting_mappings, new_new_model_df_tall, RAISE_ERROR)
    #drop the fuels cols
    new_new_model_df_tall = new_new_model_df_tall.drop(columns=['fuels', 'subfuels','reference_name'])
    
    new_new_model_df_tall = new_new_model_df_tall.rename(columns={'plotting_name': 'fuels_plotting'})
    return new_new_model_df_tall


def merge_transformation_sector_mappings(model_df_tall, transformation_sector_mappings,new_fuel_plotting_mappings, RAISE_ERROR=True):
    """this function will merge the transformation_sector_mappings dataframe to the model_df_tall dataframe. It will then join the new_fuel_plotting_mappings dataframe to the model_df_tall dataframe. It will then create two dataframes based on the input and output fuels from the transformation sector (see 'input_fuel' below)). It will then check that no sectors_plotting values from transformation_sector_mappings have been lost in the merge, if so, let user know. Finally it will drop the fuels cols and return the two dataframes.

    input_fuel: col which is a bool and determines whether we are looking for input or output fuels from the transformation sector. If is input then the values need to be negative, if output then positive (We'll filter for this)
    
    Args:
        model_df_tall (_type_): _description_
        transformation_sector_mappings (_type_): _description_
        new_fuel_plotting_mappings (_type_): _description_
        RAISE_ERROR (bool, optional): _description_. Defaults to True.

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """

    model_df_transformation = model_df_tall.copy()
    #join the transformation_sector_mappings dataframe to the model_df_tall_transformation dataframe
    model_df_transformation = model_df_transformation.merge(transformation_sector_mappings, how='right', on=['sectors','sub1sectors'])

    #and join the fuel_plotting mapping to the df 
    new_model_df_transformation = model_df_transformation.copy()
    #empty it
    new_model_df_transformation = new_model_df_transformation[0:0]

    #so join the new_sector_plotting_mappings to the model_df_tall
    for unique_col in new_fuel_plotting_mappings.reference_name_column.unique():
        columns_data = new_fuel_plotting_mappings[new_fuel_plotting_mappings.reference_name_column == unique_col][['plotting_name', 'reference_name']]
        
        #filter for the unique col and then join on the unique col to the model_df_tall
        columns_data = model_df_transformation.merge(columns_data, how='inner', left_on=unique_col, right_on='reference_name')
        #rename plotting_name to fuels_plotting
        columns_data = columns_data.rename(columns={'plotting_name': 'fuels_plotting'})
        #concat to the new_model_df_tall
        new_model_df_transformation = pd.concat([new_model_df_transformation, columns_data])
    
    #now separaten into input and output dfs using the boolean and whtehr value is positive or negative
    input_transformation = new_model_df_transformation[(new_model_df_transformation['input_fuel'] == True) & (new_model_df_transformation['value'] <= 0)].copy()
    input_transformation['value'] = input_transformation['value'] * -1

    output_transformation = new_model_df_transformation[(new_model_df_transformation['input_fuel'] == False) & (new_model_df_transformation['value'] >= 0)].copy()
    
    #check that no sectors_plotting values from transformation_sector_mappings have been lost
    new_df = new_model_df_transformation[['sectors_plotting', 'sectors', 'sub1sectors']].drop_duplicates().replace('x', np.nan)
    mapping = transformation_sector_mappings[['sectors_plotting', 'sectors', 'sub1sectors']].drop_duplicates() 
    # Merge the dataframes and add an indicator column
    merged_df = pd.merge(new_df, mapping, on=['sectors_plotting', 'sectors', 'sub1sectors'], how='outer', indicator=True)
    # Find rows that are only in mapping
    missing_in_new_model = merged_df[merged_df['_merge'] == 'right_only']
    #TODO WE SEEM TO BE MISSING TRANSFORMATION SECTORS. I GUESS ITS SOME ISSUE IN EBT. i.e. we are missing 09_04_electric_boilers. I think its dealt with in workflow\scripts\C_subset_data.py line 223. but i dont knwo how that code works
    if len(missing_in_new_model) > 0:
        if RAISE_ERROR:
            raise Exception('There are sectors_plotting values that have been lost in the merge. These are: ', missing_in_new_model)
        print('There are sectors_plotting values that have been lost in the merge. These are: ', missing_in_new_model)
    #drop the fuels cols
    input_transformation = input_transformation.drop(columns=['sectors', 'sub2sectors', 'sub4sectors', 'sub1sectors', 'sub3sectors', 'fuels', 'subfuels','reference_name', 'input_fuel'])
    output_transformation = output_transformation.drop(columns=['sectors', 'sub2sectors', 'sub4sectors', 'sub1sectors', 'sub3sectors', 'fuels', 'subfuels','reference_name', 'input_fuel'])
    
    return input_transformation, output_transformation

def merge_capacity_mappings(model_df_tall, new_capacity_plotting_mappings, capacity_plotting_mappings, RAISE_ERROR=True):
    """grab data from the original model df_tall for capacity. since we are reporting capacity by sector we search for rows which match the sectors_plotting column in the capacity_plotting_mappings dataframe. This is realtively simple because we only need to do it on sectors.

    Note the addition of sheet column to help differentiate the same rows from different sheets. 
    Args:
        model_df_tall (_type_): _description_
        new_capacity_plotting_mappings (_type_): _description_
        capacity_plotting_mappings (_type_): _description_
        RAISE_ERROR (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    new_model_df_tall = model_df_tall.copy()
    new_model_df_tall = new_model_df_tall[0:0]  # Empty it
    
    #UNIQUE TO CAPACITY MAPPING, WE NEED TO INSERT EH AGGREGATE NAME INTO THE CAPACITY PLOTTING MAPPINGS. WE DO THIS BY JOINING ON THE PLOTTING NAME:
    plotting_name = new_capacity_plotting_mappings['plotting_name_column'].unique()[0]
    plotting_name_to_aggregate_name = capacity_plotting_mappings[[plotting_name, 'aggregate_name']].drop_duplicates()
    new_capacity_plotting_mappings = new_capacity_plotting_mappings.merge(plotting_name_to_aggregate_name, how='left', left_on='plotting_name', right_on=plotting_name)
    for unique_col, sheet in new_capacity_plotting_mappings[['reference_name_column', 'sheet']].drop_duplicates().values:
        columns_data = new_capacity_plotting_mappings[(new_capacity_plotting_mappings['reference_name_column'] == unique_col) & (new_capacity_plotting_mappings['sheet'] == sheet)]
        columns_data = columns_data[['plotting_name', 'reference_name', 'aggregate_name', 'sheet']]
        columns_data = model_df_tall.merge(columns_data, how='inner', left_on=[unique_col,'sheet'], right_on=['reference_name','sheet'])
        new_model_df_tall = pd.concat([new_model_df_tall, columns_data])
    try:
        check_missing_plotting_name_values_when_merging_mappings_to_modelled_data([ 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors','sub4sectors', 'sheet'], new_capacity_plotting_mappings['plotting_name_column'].unique()[0], new_capacity_plotting_mappings, capacity_plotting_mappings, new_model_df_tall, RAISE_ERROR=False)
    except Exception as e:
        check_missing_plotting_name_values_when_merging_mappings_to_modelled_data([ 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors','sub4sectors', 'sheet'], new_capacity_plotting_mappings['plotting_name_column'].unique()[0], new_capacity_plotting_mappings, capacity_plotting_mappings, new_model_df_tall, RAISE_ERROR=False)
    # Drop unnecessary columns
    new_model_df_tall = new_model_df_tall.drop(columns=['sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'reference_name'])

    new_model_df_tall = new_model_df_tall.rename(columns={'plotting_name': 'capacity_plotting'})
    
    return new_model_df_tall


def format_plotting_df_from_mapped_plotting_names(plotting_df, new_charts_mapping):
    """We need to transfer from having data that is set into all possible plotting name compbinations (i.e. for energy contains a fuels plotting name and sectors plotting name) to a dataset that has the 'aggregate_name_column', 'aggregate_name', 'plotting_name_column', 'plotting_name' columns. This will need to be done by mapping the plotting_df to new_charts_mapping. 
    
    The new_charts_mapping dataframe contains the 'aggregate_name_column', 'aggregate_name', 'plotting_name_column', 'plotting_name' columns, and is the  structure we want in the final df. 
    
    Plotting df contains all the data needed to plot the plots but isnt in the right structure, so we need to map it to the new_charts_mapping dataframe.
    
    The output of this function is a dataframe with all the required data we can extract form this plotting_df, and the structure we want in the final df to plot the plots."""
    #get all unique combinations in aggregate_name_column and plotting_name_column, these are the unique columns we will pull data from:
    unique_aggregate_name_column_plotting_name_column_combinations = new_charts_mapping[['aggregate_name_column', 'plotting_name_column', 'source']].drop_duplicates()
    plotting_df_mapped = pd.DataFrame()
    
    for aggregate_name, plotting_name, source in zip(unique_aggregate_name_column_plotting_name_column_combinations['aggregate_name_column'], unique_aggregate_name_column_plotting_name_column_combinations['plotting_name_column'], unique_aggregate_name_column_plotting_name_column_combinations['source']):
        #check if source is in plotting_df, if its not then skip this mapping
        if source not in plotting_df['source'].unique():
            continue
        #extract those rows from new_charts_mapping, set their aggregate_name and plotting_name cols to the  aggregate_name and plotting_name variables, and then merge with plotting_df on the newly named plotting_name and aggregate_name cols:
        new_charts_mapping_subset = new_charts_mapping[(new_charts_mapping['aggregate_name_column'] == aggregate_name) & (new_charts_mapping['plotting_name_column'] == plotting_name) & (new_charts_mapping['source'] == source)].copy()
        new_charts_mapping_subset.rename(columns={'aggregate_name':aggregate_name, 'plotting_name':plotting_name}, inplace=True)
        
        #PLEASE NOTE THAT THIS IS WHERE WE MERGE THE MAPPINGS WITH THE DATA, SO ITS ONE OF THE MOST IMPORTANT STEPS IN THE WHOLE PROCESS.
        plotting_df_subset = plotting_df.merge(new_charts_mapping_subset, how='right', on=[aggregate_name, plotting_name, 'source'], indicator=True)
        #check that there are no right only rows, if there are then raise an warning since this is where we have no available data for the plotting_name and aggregate_name combination. then remove them from the plotting_df_subset and drop the _merge col
        if plotting_df_subset[plotting_df_subset['_merge'] == 'right_only'].shape[0] > 0:
            print('\nWARNING: There are plotting_name and aggregate_name combinations that have no data. These are: \n', plotting_df_subset[plotting_df_subset['_merge'] == 'right_only'])
            plotting_df_subset = plotting_df_subset[plotting_df_subset['_merge'] != 'right_only']
        plotting_df_subset = plotting_df_subset.drop(columns=['_merge'])
        
        #now we have all the data from plotting_df for this aggregate_name and plotting_name combination. so rename and concat
        plotting_df_subset = plotting_df_subset.rename(columns={aggregate_name:'aggregate_name', plotting_name:'plotting_name'})
        
        #filter fo ronly the cols we need:
        plotting_df_subset = plotting_df_subset[['source', 'economy','table_number','sheet_name', 'chart_type', 'chart_title', 'plotting_name_column', 'plotting_name','aggregate_name_column', 'aggregate_name', 'scenarios', 'year', 'table_id', 'value']]
        
        plotting_df_mapped = pd.concat([plotting_df_mapped, plotting_df_subset])
    #filter rfor the cols we want
    plotting_df_mapped = plotting_df_mapped.groupby(['source', 'economy','table_number','sheet_name', 'chart_type', 'chart_title', 'plotting_name_column', 'plotting_name','aggregate_name_column', 'aggregate_name', 'scenarios', 'year', 'table_id']).sum().reset_index()               
    return plotting_df_mapped



def format_chart_titles(charts_mapping, ECONOMY_ID):
    #charts titles use {VARIABLE} to indicate where the variable name should be inserted. This function replaces {VARIABLE} with the variable name, which may be based on either the value for that row or a varaible like economy_id
    
    def map_variable_to_value(row, ECONOMY_ID):
        #this function will map the variable to the value for that row. If the  lower case version of the variable is a column in the row, it will map the value in that column. If the variable is a string, it will map that to a varaible if it has a mapping below:
        
        #first check if there are any {VARIABLE} in the chart_title col, if not then return the variable. Note that VARIABLE represents any sequence of lower or uppercase characters, so it could be any variable name, so use regex to find it
        # a = '{sdd_32saDD} {fsdhsu_32435fh} ssd' #example of a string that would match
        varaibles_in_chart_title = re.findall(r'{[a-zA-Z_0-9]*}', row['chart_title'])
        if len(varaibles_in_chart_title) == 0:
            return row['chart_title']
        variables = [x.replace('{', '').replace('}', '') for x in varaibles_in_chart_title]
        
        for var in variables:
            if var.lower() in row.index:
                row['chart_title'] = row['chart_title'].replace('{'+var+'}', str(row[var.lower()]))
            elif var == 'ECONOMY_ID':
                row['chart_title'] = row['chart_title'].replace('{'+var+'}', ECONOMY_ID)
            else:
                print('The variable {} in the chart_title column is not recognised'.format(var))
        return row['chart_title']
    
    charts_mapping['chart_title'] = charts_mapping.apply(lambda row: map_variable_to_value(row, ECONOMY_ID), axis=1)
    
    return charts_mapping

def modify_dataframe_content(all_model_df_wides_dict, source, modification_func):
    """
    Modifies the content of the EBT for a specified source using a given modification function.

    Parameters:
    - all_model_df_wides_dict (dict): A dictionary containing sources as keys and lists with file paths and dataframes as values.
    - source (str): The source key for which the dataframe should be modified.
    - modification_func (function): A function that takes a dataframe as input and returns a modified dataframe.

    Returns:
    - all_model_df_wides_dict (dict): The updated dictionary with the modified dataframe.
    """
    if source in all_model_df_wides_dict:
        # Retrieve the current dataframe
        current_df = all_model_df_wides_dict[source][1]
        # Apply the modification function to the dataframe
        modified_df = modification_func(current_df)
        # Update the dictionary with the modified dataframe
        all_model_df_wides_dict[source][1] = modified_df
        print(f"Dataframe for source '{source}' has been modified.")
    else:
        print(f"Source '{source}' not found in the dictionary.")

    return all_model_df_wides_dict

# Modification functions
def modify_losses_and_own_use_values(df):
    """
    Changes the numeric values in the year columns for rows where the 'sectors' column
    is '10_losses_and_own_use' from negative to positive.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    # Identifying year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Filtering rows where the 'sectors' column is '10_losses_and_own_use'
    condition = df['sectors'] == '10_losses_and_own_use'

    # Changing values from negative to positive for the identified rows and year columns
    df.loc[condition, year_columns] = df.loc[condition, year_columns].abs()

    return df

def convert_electricity_output_to_twh(df):
    """
    Converts values from GWh to TWh in the year columns for rows where the 'sectors' column
    is '18_electricity_output_in_gwh' by dividing them by 1000.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    # Identifying year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Filtering rows where the 'sectors' column is '18_electricity_output_in_gwh'
    condition = df['sectors'] == '18_electricity_output_in_gwh'

    # Dividing values by 1000 for the identified rows and year columns to convert GWh to TWh
    df.loc[condition, year_columns] = df.loc[condition, year_columns] / 1000

    return df

def copy_and_modify_rows_with_conversion(df):
    """
    Finds rows with specific criteria, copies them, modifies certain values including converting
    energy values from PJ to TWh, and appends the modified rows to the dataframe.

    The specific criteria are:
    - 'sectors' == '02_imports'
    - 'fuels' == '17_electricity'
    - 'sub1sectors' == 'x'

    The modifications for the copied rows are:
    - 'sectors' is changed to '18_electricity_output_in_gwh'
    - 'sub1sectors' is changed to '18_01_electricity_plants'
    - 'fuels' is changed to '19_imports'
    - Values in year columns are converted from PJ to TWh by multiplying by 0.277778.

    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe with the new rows added.
    """
    # Find rows that match the criteria
    criteria = (df['sectors'] == '02_imports') & (df['fuels'] == '17_electricity') & (df['sub1sectors'] == 'x')
    matching_rows = df[criteria]
    # matching_rows.to_csv('../intermediate_data/matching_rows.csv')

    # Identify year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Copy the matching rows and modify specified columns
    if not matching_rows.empty:
        new_rows = matching_rows.copy()
        new_rows['sectors'] = '18_electricity_output_in_gwh'
        new_rows['sub1sectors'] = 'x'
        new_rows['fuels'] = '22_imports'

        # Convert values from PJ to TWh for the year columns in the new rows
        conversion_factor = 0.277778  # 1 PJ = 0.277778 TWh
        new_rows[year_columns] = new_rows[year_columns] * conversion_factor
    else:
        # Create new rows with 0 values if no matching rows
        new_rows = pd.DataFrame([{
            **{col: matching_rows.iloc[0][col] if col not in year_columns else 0 for col in df.columns},
            'sectors': '18_electricity_output_in_gwh',
            'sub1sectors': 'x',
            'fuels': '22_imports'
        }])

    # new_rows.to_csv('../intermediate_data/new_rows.csv')

    # Append the new rows to the original dataframe
    modified_df = pd.concat([df, new_rows], ignore_index=True)

    # modified_df.to_csv('../intermediate_data/modified_df.csv')

    return modified_df

def modify_gas_to_gas_ccs(df):
    """
    Searches for rows with '18_01_02_gas_power_ccs' under 'sub2sectors' column and changes
    '08_gas' under 'fuels' column to '08_gas_ccs'.
    Additionally, searches for rows with '14_03_01_03_ccs', '14_03_02_02_ccs', or '14_03_04_01_ccs' 
    under 'sub3sectors' column and changes '08_gas' under 'fuels' column to '08_gas_ccs'.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    # Define the condition for the rows to modify in sub2sectors
    condition_sub2 = (df['sub2sectors'] == '18_01_02_gas_power_ccs') & (df['fuels'] == '08_gas')
    
    # Define the condition for the rows to modify in sub3sectors
    condition_sub3 = (df['sub3sectors'].isin(['14_03_01_03_ccs', '14_03_02_02_ccs', '14_03_04_01_ccs'])) & (df['fuels'] == '08_gas')
    
    # Combine both conditions
    condition = condition_sub2 | condition_sub3
    
    # Apply the modification
    df.loc[condition, 'fuels'] = '08_gas_ccs'

    return df

def modify_hydrogen_green_electricity(df):
    """
    Searches for a row where it is '09_total_transformation_sector' in 'sectors',
    '09_13_hydrogen_transformation' in 'sub1sectors', '09_13_01_electrolysers' in 'sub2sectors' and '17_x_green_electricity' in 'fuels',
    and changes the 'sub1sectors' from '09_13_hydrogen_transformation' to '09_13x_hydrogen_transformation'.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    # Define the condition for the rows to modify
    condition = (df['sectors'] == '09_total_transformation_sector') & \
                (df['sub1sectors'] == '09_13_hydrogen_transformation') & \
                (df['sub2sectors'] == '09_13_01_electrolysers') & \
                (df['fuels'] == '17_x_green_electricity')
    
    # Apply the modification
    df.loc[condition, 'sub1sectors'] = '09_13x_hydrogen_green_electricity'

    return df

# Temporary fix to exclude hydrogen in ccs emissions
def drop_hydrogen_transformation_rows(df):
    """
    Drops rows from the DataFrame where 'sub1sectors' is '09_13_hydrogen_transformation'.

    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe with specified rows dropped.
    """
    # Define the condition for rows to drop
    condition = df['sub1sectors'] == '09_13_hydrogen_transformation'
    
    # Drop rows that match the condition
    df = df[~condition]

    return df

def rename_sectors_and_negate_values_based_on_ccs_cap(df):
    """
    For rows with a suffix '_ccs_cap' in 'sub2sectors' or 'sub3sectors' columns:
    - Adds '_emissions_cap' to the suffix of the category name in the 'sectors' column and ensures values in year columns are negative.
    - Copies these rows, renames the category in 'sectors' to '_emissions_cap_pos', and makes the year values positive.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe with additional rows appended.
    """
    # Identify year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Define condition for rows to modify
    condition = df['sub2sectors'].str.endswith('_ccs_cap') | df['sub3sectors'].str.endswith('_ccs_cap')
    
    # Copy the rows that meet the condition, to modify and append them
    rows = df.loc[condition].copy()
    
    # Update 'sectors' and year values for rows matching the condition
    rows.loc[condition, 'sectors'] = rows.loc[condition, 'sectors'] + '_emissions_cap_neg'
    for col in year_columns:
        rows.loc[condition, col] = rows.loc[condition, col].apply(lambda x: -abs(x))

    # Copy the rows that meet the condition, to modify and append them
    new_rows = rows.loc[condition].copy()
    new_rows['sectors'] = new_rows['sectors'].str.replace('_emissions_cap_neg', '_emissions_cap_pos')
    for col in year_columns:
        new_rows[col] = new_rows[col].abs()  # Make values positive
    
    # Copy new rows and rename the category in 'sectors' to '_emissions_area'
    new_rows_area = new_rows.copy()
    new_rows_area['sectors'] = new_rows_area['sectors'].str.replace('_emissions_cap_pos', '_emissions_area')

    # Concatenate the new rows to the original dataframe
    df = pd.concat([df, rows, new_rows, new_rows_area], ignore_index=True)

    return df

def copy_and_modify_power_sector_rows(df):
    """
    Copies rows where 'sub1sectors' matches certain criteria and has negative values,
    renames 'sectors' by adding '_net' to the end, turns the year values positive,
    then appends them to the dataframe.
    """
    # Define the list of 'sub1sectors' values to filter
    power_sectors = [
        '09_01_electricity_plants',
        '09_02_chp_plants',
        '09_04_electric_boilers',
        '09_05_chemical_heat_for_electricity_production',
        '09_x_heat_plants'
    ]

    # Identify year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Filter rows where 'sub1sectors' matches the criteria and has negative values in any year column
    condition = (df['sectors'] == '09_total_transformation_sector') & df['sub1sectors'].isin(power_sectors) & (df[year_columns] < 0).any(axis=1)

    # Filter rows matching the condition
    filtered_rows = df[condition].copy()

    # Modify 'sectors' by adding '_net' to the end
    filtered_rows['sectors'] += '_net'

    # Ensure all values in year columns are positive
    filtered_rows[year_columns] = filtered_rows[year_columns].abs()

    # Append the modified rows to the original dataframe
    df = pd.concat([df, filtered_rows], ignore_index=True)

    return df

def modify_subtotal_columns(df):
    """
    Modifies the 'subtotal_layout' and 'subtotal_results' columns by setting it to True for specific rows based on the conditions.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    # Define the conditions for the rows to modify
    conditions = (
        ((df['sectors'] == '14_industry_sector') & (df['sub1sectors'] != 'x') & (df['fuels'] == '20_total_renewables')) |
        ((df['sectors'] == '15_transport_sector') & (df['sub1sectors'] != 'x') & (df['fuels'] == '20_total_renewables')) |
        ((df['sectors'] == '16_other_sector') & (df['sub1sectors'] == '16_01_buildings') & (df['sub2sectors'] != 'x') & (df['fuels'] == '20_total_renewables')) |
        ((df['sectors'] == '16_other_sector') & (df['sub1sectors'] == 'x') & (df['fuels'] == '20_total_renewables'))
    )

    # Apply the modifications
    df.loc[conditions, ['subtotal_layout', 'subtotal_results']] = True

    return df

# Function to add percentage_bar chart_type in the dataframe
def add_percentage_bar_chart_type(df):
    # Filter the rows where chart_type is 'area' or 'line'
    filtered_df = df[df['chart_type'].isin(['area', 'line'])].copy()
    
    # Drop duplicates based on 'scenario', 'year', 'plotting_name', and 'table_id'
    filtered_df.drop_duplicates(subset=['scenario', 'year', 'plotting_name', 'table_id'], inplace=True)
    
    # Create a copy of the filtered rows with chart_type set to 'percentage_bar'
    new_rows = filtered_df.copy()
    new_rows['chart_type'] = 'percentage_bar'
    
    # Append the new rows to the original dataframe
    modified_df = pd.concat([df, new_rows], ignore_index=True)
    
    # Reset the index of the dataframe
    modified_df.reset_index(drop=True, inplace=True)
    
    return modified_df

# def collect_missing_datapoints(economy_new_charts_mapping):
#     #now loop through the unique sheet, table combinations and idneitfy if there are any missing values (nas) in the value col. Put the data for these into a new dataframe called missing_data
#     missing_data = pd.DataFrame()
#     na_data = economy_new_charts_mapping[economy_new_charts_mapping.value.isna()]
#     for table_id in economy_new_charts_mapping.table_id.unique():
#         if table_id in na_data.table_id.unique():
#             missing_data = pd.concat([missing_data, na_data[na_data.table_id == table_id]])
#     return missing_data, economy_new_charts_mapping

# def check_for_duplicates_in_plotting_names(new_sector_plotting_mappings, new_fuel_plotting_mappings, RAISE_ERROR=True):
#     #this is important because??
    
#     plotting_names = new_sector_plotting_mappings['sectors_plotting'].unique().tolist() + new_fuel_plotting_mappings['fuels_plotting'].unique().tolist()
#     #identify if there are any duplicates in the plotting names
#     duplicates = [item for item, count in collections.Counter(plotting_names).items() if count > 1]
#     if len(duplicates) > 0:
#         if RAISE_ERROR:
#             raise Exception('There are plotting names that are duplicated between fuels and sectors. Please check the following plotting names: ', duplicates)
#         else:
#             print('There are plotting names that are duplicated between fuels and sectors. You might want to check the following plotting names: ', duplicates)

#     return set(plotting_names)
    
# def prepare_color_plot(colors_df):

#     # Create labels and colors lists
#     labels = colors_df.plotting_name
#     colors = colors_df.color

#     #identify any duplicate labels
#     if labels[labels.duplicated()].empty == False:
#         raise ValueError('Duplicate labels found in the colors_df dataframe', labels[labels.duplicated()])
    
#     #create dict
#     colors_dict = dict(zip(labels, colors))
    
#     plot_color_grid(colors_dict)
#     plot_color_wheel(colors_dict)
    
# def plot_color_wheel(colors_dict):
    
#     #Convert to the HSV color space and sort by hue:
#     # Function to convert hex color to RGB
#     def hex_to_rgb(hex_color):
#         hex_color = hex_color.lstrip('#')
#         return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))

#     # Function to convert RGB color to HSV
#     def rgb_to_hsv(rgb_color):
#         return colorsys.rgb_to_hsv(*rgb_color)

#     # Convert colors to HSV and create a list of (label, color, hsv) tuples
#     color_tuples = [(label, color, rgb_to_hsv(hex_to_rgb(color))) for label, color in colors_dict.items()]

#     # Sort by hue
#     color_tuples.sort(key=lambda x: x[2][0])

#     # Create labels and colors lists from sorted tuples
#     labels = [t[0] for t in color_tuples]
#     colors = [t[1] for t in color_tuples]

#     # Create an array of angles evenly spaced around a circle
#     angles = np.linspace(0, 2 * np.pi, len(labels) + 1)

#     # Create a trace for the polar chart
#     trace = go.Barpolar(
#         r=[1] * len(labels),  # All bars have the same length
#         theta=angles * 180 / np.pi,  # Convert angles to degrees
#         width=[np.diff(angles)[0]] * len(labels),  # All bars have the same width
#         marker=dict(color=colors),
#         text=labels,
#         hoverinfo='text',
#         showlegend=False
#     )

#     # Create the layout for the plot
#     layout = go.Layout(
#         title='Color Wheel Representation',
#         polar=dict(
#             radialaxis=dict(visible=False),
#             angularaxis=dict(visible=False),
#         ),
#         paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
#     )

#     # Create the figure and add the trace
#     fig = go.Figure(data=[trace], layout=layout)

#     # write the figure to html
#     fig.write_html("../config/plotting_names_color_wheel.html")
    
    
# def plot_color_grid(colors_dict):
        
#     # Determine grid size based on number of colors
#     n = len(colors_dict)
#     cols = round(math.sqrt(n))
#     rows = cols if cols * cols >= n else cols + 1

#     # Create subplot matrix with invisible plots
#     fig = make_subplots(rows=rows, cols=cols)

#     # Create labels and colors lists
#     labels = list(colors_dict.keys())
#     colors = list(colors_dict.values())

#     # Fill subplots with colors
#     for i in range(rows):
#         for j in range(cols):
#             index = i * cols + j
#             if index < n:
#                 fig.add_trace(
#                     go.Scatter(x=[0, 1], y=[0, 1], mode='text',
#                             text=[labels[index]], showlegend=False,
#                             textposition='middle center'),
#                     row=i + 1, col=j + 1
#                 )
#                 fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, visible=False, row=i + 1, col=j + 1)
#                 fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, visible=False, row=i + 1, col=j + 1)
#                 fig.add_layout_image(
#                     dict(
#                         source="data:image/svg+xml;base64,CiAgPHN2ZyB3aWR0aD0iMCIgaGVpZ2h0PSIwIj4KICAgIDxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiN7fSIvPgogIDwvc3ZnPgo=".format(colors[index]),
#                         xref="x{}".format(index+1),
#                         yref="y{}".format(index+1),
#                         x=0,
#                         y=1,
#                         sizex=1,
#                         sizey=1,
#                         sizing="stretch",
#                         layer="below"
#                     )
#                 )
#     # write the figure to html
#     fig.write_html("../config/plotting_names_color_grid.html")








    # for aggregate_name_column in aggregate_name_columns:
    #     # Select the current aggregate column
    #     current_aggregate_name = charts_mapping[charts_mapping['aggregate_name_column'] == aggregate_name_column]['aggregate_name'].iloc[0]

    #     # Filter the DataFrame for the current aggregate
    #     aggregated = charts_mapping[charts_mapping['aggregate_name_column'] == aggregate_name_column]

    #     # Determine the plotting columns (group 3 columns)
    #     group_3_cols = [x for x in charts_mapping.columns if x not in key_cols + ['aggregate_name_column', 'aggregate_name']]

    #     # Melt the dataframe on group 3 columns
    #     melted = pd.melt(aggregated, id_vars=key_cols + ['aggregate_name_column', 'aggregate_name'], value_name='plotting_name', var_name='digits')

    #     # Drop the 'digits' column and any NAs in the 'plotting_name' column
    #     melted.drop(columns=['digits'], inplace=True)
    #     melted.dropna(subset=['plotting_name'], inplace=True)

    #     # Add a column to identify the aggregate column
    #     melted['aggregate_name_column'] = aggregate_name_column
    #     melted['aggregate_name'] = current_aggregate_name

    #     # Append to the final DataFrame
    #     new_charts_mapping = pd.concat([new_charts_mapping, melted], ignore_index=True)

    # # Create a unique identifier for each sheet and table number
    # new_charts_mapping['table_id'] = new_charts_mapping['sheet_name'] + '_' + new_charts_mapping['table_number'].astype(str)

    # return new_charts_mapping


# def format_charts_mapping(charts_mapping):
#     #this df has a unique format that isnt easy to work with. Firstly, the top row is a header to make it easy to fill in manually, so drop it. Then on the next rwo are three gorups of cols essentially, each with a different purpose.
#     #group 1: sheet_name	table_number	chart_type
#     #group 2 (the aggregate): fuels_plotting	sectors_plotting
#     #group 3 (plotting_names): (which are just numbers from 0 onwards)
#     #leave group 1 as is.
#     # for group 2, we will split the dataframe depending on if fuels plotting or sectors plotting is na. if neither or both , throw and error. if one or the other, then we will have a df 'fuels_plotting' which is where fuels_plotting is na (hterefore sectors plotting is the aggregate), and sectors_plotting which is where sectors_plotting is na (therefore fuels plotting is the aggregate)
#     #then for both of these we will deal with group 3 in the same way:
#     #for group 3, drop the column in fuels_plotting or sectors_plotting that is na(this is the plotting name column). set 'plotting name' to the name of the col that is na (eg. plotting_name  = 'fuels_plotting' if the column fuels plotting is na and sectors plotting is the aggregate). then melt the dataframe so that the group 3 columns (plotting name cols) are all in one col. drop the col names (the digits) and drop nas from the new col
#     #then concat the two dfs together!
    
#     #every column after: [sheet	table_number	chart_type ] will be melted into a plotting_name column. then remove nas from plotting_name column
#     #but to be safe, double check that these columns are just digits, becuase if there are new cols added, this will break
#     key_cols = ['sheet_name', 'table_number', 'chart_type', 'chart_title']
#     group_2_cols = ['fuels_plotting', 'sectors_plotting']
#     group_3_cols = [x for x in charts_mapping.columns.tolist() if x not in key_cols + group_2_cols]
#     if not all([str(x).isdigit() for x in group_3_cols]):
#         raise Exception('plotting name columns are not all named with digits')
            
#     # for group 2, we will split the dataframe depending on if fuels plotting or sectors plotting is na. if both, then we will have a df 'fuels_plotting' which is where fuels_plotting is not na,, and sectors_plotting which is where sectors_plotting is not na.
#     check_charts_mapping_group_2_cols(charts_mapping)
#     temp_dict = {} 
#     temp_dict['charts_mapping_sectors_plotting'] = charts_mapping.dropna(subset=['sectors_plotting'])
#     temp_dict['charts_mapping_fuels_plotting'] = charts_mapping.dropna(subset=['fuels_plotting'])
    
#     #for group 3, drop the column in fuels_plotting or sectors_plotting that is na. set 'plotting name' to the name of the col that is not na (eg. plotting_name  = 'fuels_plotting' if the column fuels plotting is not na). then melt the dataframe so that the group 3 columns are all in one col, with the name of the col with na's. drop the col names (the digits) and drop nas from the new col
#     #then concat the two dfs together!
    
#     ######################################################
#     #where sectors_plotting is na (therefore the plotting names will be sectors):
#     aggregated_by_sector = charts_mapping.dropna(subset=['sectors_plotting'])
#     plotting_name = 'fuels_plotting'
#     aggregate_name = 'sectors_plotting'
#     aggregated_by_sector.drop(columns=[plotting_name], inplace=True)
#     aggregated_by_sector = pd.melt(aggregated_by_sector, id_vars=key_cols + [aggregate_name], value_name=plotting_name, var_name='digits')
#     aggregated_by_sector = aggregated_by_sector.drop(columns=['digits'])
#     #drop nas in plotting_name
#     aggregated_by_sector = aggregated_by_sector.dropna(subset=[plotting_name])
#     #set 'plotting_name' to plotting_name
#     aggregated_by_sector['plotting_name'] = plotting_name
#     aggregated_by_sector['aggregate_name'] = aggregate_name
    
#     #where fuels_plotting is na (therefore the plotting names will be fuels):
#     aggregated_by_fuels = charts_mapping.dropna(subset=['fuels_plotting'])
#     plotting_name = 'sectors_plotting'
#     aggregate_name = 'fuels_plotting'
#     aggregated_by_fuels.drop(columns=[plotting_name], inplace=True)
#     aggregated_by_fuels = pd.melt(aggregated_by_fuels, id_vars=key_cols + [aggregate_name], value_name=plotting_name, var_name='digits')
#     aggregated_by_fuels = aggregated_by_fuels.drop(columns=['digits'])
#     #drop nas in plotting_name
#     aggregated_by_fuels = aggregated_by_fuels.dropna(subset=[plotting_name])
#     #set 'plotting_name' to plotting_name
#     aggregated_by_fuels['plotting_name'] = plotting_name
#     aggregated_by_fuels['aggregate_name'] = aggregate_name
#     #concat the two dfs together
#     new_charts_mapping = pd.concat([aggregated_by_sector, aggregated_by_fuels])
    
#     #concat unique sheet and table_numbers cols
#     new_charts_mapping['table_id'] = new_charts_mapping['sheet_name'] + '_' + new_charts_mapping['table_number'].astype(str)

#     return new_charts_mapping

# def format_charts_mapping(charts_mapping):
#     #every column after: [sheet	table_number	chart_type ] will be melted into a plotting_name column. then remove nas from plotting_name column
#     #but to be safe, double check that these columns are just digits, becuase if there are new cols added, this will break
#     key_cols = ['sheet_name', 'table_number', 'chart_type', 'chart_title']
#     cols_after_table = [x for x in charts_mapping.columns.tolist() if x not in key_cols]
#     if not all([str(x).isdigit() for x in cols_after_table]):
#         raise Exception('columns after table are not all digits')
            
#     new_charts_mapping = charts_mapping.copy()
#     #melt the data
#     new_charts_mapping = pd.melt(new_charts_mapping, id_vars=key_cols, value_name='plotting_name', var_name='digits')
#     #drop digits
#     new_charts_mapping = new_charts_mapping.drop(columns=['digits'])
#     new_charts_mapping = new_charts_mapping.dropna(subset=['plotting_name'])

#     #concat unique sheet and table_numbers cols
#     new_charts_mapping['table_id'] = new_charts_mapping['sheet_name'] + '_' + new_charts_mapping['table_number'].astype(str)

#     return new_charts_mapping





# def format_plotting_mappings(sector_plotting_mappings, fuel_plotting_mappings):
#     #will loop through the sector_plotting_mappings and fuel_plotting_mappings and create a new df where only the most specific sector/fuel columns is referenced as teh reference_name_column (which is the column from which to look for the refererence_sector/fuel when extracting the data for the plotting_sector/fuel). Each plotting_sector/fuel might have multiple reference_sector/fuels from any number of different reference columns.
#     new_sector_plotting_mappings = pd.DataFrame(columns=['sectors_plotting', 'reference_sector', 'reference_name_column'])
#     ordered_columns = [ 'sub2sectors', 'sub1sectors','sectors']
#     for col in ordered_columns:
#         #extract rows where the value is not na in this col
#         for row in sector_plotting_mappings[sector_plotting_mappings[col].notna()].index:
#             #loop through the rows
#             row_x = sector_plotting_mappings.loc[row]
#             #create new row in new_sector_plotting_mappings
#             new_row = pd.DataFrame({'sectors_plotting': [row_x['sectors_plotting']],
#                         'reference_sector': [row_x[col]],
#                         'reference_name_column': [col]})

#             new_sector_plotting_mappings = pd.concat([new_sector_plotting_mappings, new_row], ignore_index=True)

#         #remove these rows from the sector_plotting_mappings so that we don't double count them
#         sector_plotting_mappings = sector_plotting_mappings[sector_plotting_mappings[col].isna()]

#     #do the same for fuels
#     new_fuel_plotting_mappings = pd.DataFrame(columns=['fuels_plotting', 'reference_fuel', 'reference_name_column']) 

#     ordered_columns = [ 'subfuels', 'fuels']
#     for col in ordered_columns:
#         #extract rows where the value is not na in this col
#         for row in fuel_plotting_mappings[fuel_plotting_mappings[col].notna()].index:
#             #loop through the rows
#             row_x = fuel_plotting_mappings.loc[row]
#             #create new row in new_sector_plotting_mappings
#             new_row = pd.DataFrame({'fuels_plotting': [row_x['fuels_plotting']],
#                         'reference_fuel': [row_x[col]],
#                         'reference_name_column': [col]})

#             new_fuel_plotting_mappings = pd.concat([new_fuel_plotting_mappings, new_row], ignore_index=True)

#         #remove these rows from the sector_plotting_mappings so that we don't double count them
#         fuel_plotting_mappings = fuel_plotting_mappings[fuel_plotting_mappings[col].isna()]
 
#     #now check for nas in the entire dfs
#     if new_sector_plotting_mappings.isna().sum().sum() > 0:
#         if STRICT_DATA_CHECKING:
#             raise('There are still some nas in the new_sector_plotting_mappings')
#     if new_fuel_plotting_mappings.isna().sum().sum() > 0:
#         if STRICT_DATA_CHECKING:
#             raise('There are still some nas in the new_fuel_plotting_mappings')
        
#     return new_sector_plotting_mappings, new_fuel_plotting_mappings

# def check_charts_mapping_group_2_cols(charts_mapping):
#     #filter for where sectors_plotting and fuels_plotting are both na. if there are any rows, throw an error
#     charts_mapping_nas = charts_mapping[charts_mapping['sectors_plotting'].isna() & charts_mapping['fuels_plotting'].isna()]
#     if len(charts_mapping_nas) > 0:
#         print(charts_mapping_nas)
#         raise Exception('There are rows in charts_mapping where both sectors_plotting and fuels_plotting are na. This is not allowed. Please fix this in the charts_mapping sheet in master_config.xlsx')
    
#     #then filter for where they are both not na. if there are any rows, throw an error
#     charts_mapping_nas = charts_mapping[charts_mapping['sectors_plotting'].notna() & charts_mapping['fuels_plotting'].notna()]
#     if len(charts_mapping_nas) > 0:
#         print(charts_mapping_nas)
#         raise Exception('There are rows in charts_mapping where both sectors_plotting and fuels_plotting are not na. This is not allowed. Please fix this in the charts_mapping sheet in master_config.xlsx')
