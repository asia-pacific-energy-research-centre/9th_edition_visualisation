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
import ast

def load_and_format_configs():
    # Import master_config xlsx
    plotting_specifications = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_specifications')
    plotting_name_to_label = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_name_to_label')
    colours_dict = pd.read_excel('../config/master_config.xlsx', sheet_name='colors')
    patterns_dict = pd.read_excel('../config/master_config.xlsx', sheet_name='patterns')
    with open(f'../intermediate_data/config/plotting_names_order_{FILE_DATE_ID}.pkl', 'rb') as handle:
        plotting_names_order = pickle.load(handle)
    ################################################################################
    # FORMAT CONFIGS
    ################################################################################
    # Convert into dictionary
    if len(plotting_specifications.columns) != 2:
        raise Exception('plotting_specifications must have exactly two columns')
    plotting_specifications = plotting_specifications.set_index(plotting_specifications.columns[0]).to_dict()[plotting_specifications.columns[1]]
    # format anything with [] in it as a list
    for key in plotting_specifications.keys():
        # e.g. 
        # Format the bar_years as a list
        # plotting_specifications['bar_years'] = ast.literal_eval(plotting_specifications['bar_years'])
        if '[' in str(plotting_specifications[key]) and ']' in str(plotting_specifications[key]):
            plotting_specifications[key] = ast.literal_eval(plotting_specifications[key])

    plotting_name_to_label_dict = plotting_name_to_label.set_index(plotting_name_to_label.columns[0]).to_dict()[plotting_name_to_label.columns[1]]
    colours_dict = colours_dict.set_index(colours_dict.columns[0]).to_dict()[colours_dict.columns[1]]
    patterns_dict = patterns_dict.set_index(patterns_dict.columns[0]).to_dict()[patterns_dict.columns[1]]    
    #find anything that contains 'inches' in the key, then set the key so it replaces 'inches' with 'pixels', then divide the inches by the 'dpi' key in plotting_specifications to get the pixels
    keys_ = [key for key in plotting_specifications.keys()]
    for key in keys_:
        if 'inches' in key:
            new_key = key.replace('inches', 'pixels')
            plotting_specifications[new_key] = plotting_specifications[key] * plotting_specifications['dpi']
            # plotting_specifications.pop(key)#no need to pop it, we can just not use it
    
    return plotting_specifications, plotting_name_to_label_dict, colours_dict, patterns_dict, plotting_names_order

def gather_charts_mapping_dict(ECONOMY_ID, FILE_DATE_ID,sources = ['energy', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2', 'capacity']):
    charts_mapping_1d = load_checkpoint(f'charts_mapping_1d_{ECONOMY_ID}')
    
    # Read in titles, only, from charts mapping for each available economy for the FILE_DATE_ID
    all_charts_mapping_files_dict = {}
    co2e_charts_mapping_df = pd.DataFrame()
    for source in sources:
        charts_mapping_files = [x for x in os.listdir('../intermediate_data/data/') if 'charts_mapping' in x and source in x]
        #just in case we accidentally pick up fiels from other sources that are named similarly, check that none of the others are in here:
        #if the source is emissions_co2, we should not have emissions_co2e in the list of files! (this is a bit of a manual check)
        if source == 'emissions_co2':
            charts_mapping_files = [x for x in charts_mapping_files if 'emissions_co2e' not in x]
        charts_mapping_files = [x for x in charts_mapping_files if 'pkl' in x]
        charts_mapping_files = [x for x in charts_mapping_files if FILE_DATE_ID in x]
        charts_mapping_files = [x for x in charts_mapping_files if ECONOMY_ID in x]
        if len(charts_mapping_files) > 1:
            print(f'We have more than 1 charts mapping input for the source {source}, economy {ECONOMY_ID}: {charts_mapping_files}')
        
        #also, we want to concatenate the files for emissions_ch4, emissions_co2e and emissions_no2 then cal their source emissions_co2e
        if source in ['emissions_ch4', 'emissions_co2e', 'emissions_no2']:
            pass
        else:
            all_charts_mapping_files_dict[source] = []
            
        for mapping_file in charts_mapping_files:
            charts_mapping_df = pd.read_pickle(f'../intermediate_data/data/{mapping_file}')
            
            #rename their source to emissions_co2e as well as concatenate with similar files. we will add it to the dictionary at the end
            if source in ['emissions_ch4', 'emissions_co2e', 'emissions_no2']:
                charts_mapping_df['source'] = 'emissions_co2e'
                co2e_charts_mapping_df = pd.concat([co2e_charts_mapping_df, charts_mapping_df])
            else:
                all_charts_mapping_files_dict[source].append(charts_mapping_df)

    #add the co2e charts mapping to the dictionary
    if len(co2e_charts_mapping_df) > 0:
        all_charts_mapping_files_dict['emissions_co2e'] = [co2e_charts_mapping_df]

    if len(charts_mapping_files) == 0:
        breakpoint()
        raise Exception('No charts mapping files found for FILE_DATE_ID: {}, ECONOMY_ID: {}'.format(FILE_DATE_ID, ECONOMY_ID))

    # Add the unique sources from charts_mapping_1d to all_charts_mapping_files_dict
    for source in charts_mapping_1d.source.unique():
        all_charts_mapping_files_dict[source] = [charts_mapping_1d[charts_mapping_1d.source == source]]
    
    return all_charts_mapping_files_dict

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

def find_and_load_latest_data_for_all_sources(ECONOMY_ID, sources, WALK=True): 
    # Initialize variables
    all_file_paths = []
    folder =f'../input_data/{ECONOMY_ID}/'
    all_model_df_wides_dict = {}
    
    # Fetch file paths based on the configuration
    if WALK:
        for root, dirs, files in os.walk(folder):
            all_file_paths.extend([os.path.join(root, file) for file in os.listdir(root) if os.path.isfile(os.path.join(root, file))])
    else:
        all_file_paths = [os.path.join(folder, file) for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]
    # Check if files are found
    if not all_file_paths:
        raise Exception(f"No file found for {folder}")

    #find latest files for each source:
    all_files_with_source = []
    for source in sources:
        all_file_paths_source = [file_path for file_path in all_file_paths if source in os.path.basename(file_path)]
        
        #########CHECK##########
        #if the source is emissions_co2, we should not have emissions_co2e in the list of files! (this is a bit of a manual check)
        if source == 'emissions_co2':
            all_file_paths_source = [x for x in all_file_paths_source if 'emissions_co2e' not in x]
        #########CHECK##########
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
        #double check there are no columns with Unnamed in them
        if all_model_df_wides_dict[source][1].columns.str.contains('Unnamed').any():
            raise ValueError(f'There are columns with Unnamed in them in the {source} file. Please remove these columns')
        
        all_model_df_wides_dict[source][1] = ensure_all_year_cols_are_int(all_model_df_wides_dict[source][1])
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
        try:
            new_charts_mapping.loc[new_charts_mapping['source'] == source, 'plotting_name_column'] = new_charts_mapping['aggregate_name_column'].map(source_and_aggregate_name_column_to_plotting_name_column_mapping_dict[source])
        except KeyError:
            breakpoint()
            new_charts_mapping.loc[new_charts_mapping['source'] == source, 'plotting_name_column'] = new_charts_mapping['aggregate_name_column'].map(source_and_aggregate_name_column_to_plotting_name_column_mapping_dict[source])
        if new_charts_mapping.loc[(new_charts_mapping['source'] == source) &(new_charts_mapping.plotting_name_column.isna())].shape[0] > 0:
            breakpoint()
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
        ##check for duplicates in plotting_names_order[table_id]. if there are throw an error since this indicates we should combine them, i think. 
        if len(plotting_names_order[table_id]) != len(set(plotting_names_order[table_id])):
            breakpoint()  
            raise ValueError('There are duplicates in the plotting_names_order for table_id: ', table_id, 'These are: ', [item for item, count in collections.Counter(plotting_names_order[table_id]).items() if count > 1])
        
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
        breakpoint()
        #provide them in a csv for easy use:
        pd.DataFrame(list(different_names)).to_csv('../missing_plotting_names.csv', index=False, header=['Missing Plotting Names'])
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


def split_gas_imports_exports_by_economy(df, ECONOMIES_TO_SPLIT_DICT={'01_AUS': 'Australia', '03_CDA': 'Canada', '04_CHL': 'Chile', '08_JPN': 'Japan', '09_ROK':'Republic of Korea', '11_MEX': 'Mexico', '20_USA': 'United States of America', '02_BD':'Brunei Darussalam', '05_PRC': 'China', '06_HKC':'Hong Kong, China', '10_MAS':'Malaysia', '12_NZ':'New Zealand', '13_PNG': 'Papua New Guinea', 'Peru':'14_PE','17_SGP': 'Singapore', '15_PHL':'Philippines', '16_RUS':'Russia', '18_CT':'Chinese Taipei', '19_THA':'Thailand', '21_VN':'Vietnam'}):#', #PLEASE NOTE THAT WE HAVE ADDED A NUMBR OF NON OECD COUNTRIES TO THE MIX.
    """
    'Australia', 'Brunei Darussalam', 'Canada', 'Chile', 'China',
    'Hong Kong, China', 'Indonesia', 'Japan', 'Republic of Korea',
    'Malaysia', 'Mexico', 'New Zealand', 'Papua New Guinea', 'Peru',
    'Philippines', 'Russia', 'Singapore', 'Chinese Taipei', 'Thailand',
    'United States of America', 'Vietnam']
    Splits the gas supply into LNG and pipeline gas for OECD countries and filters data before the OUTLOOK_BASE_YEAR.
    
    Data is from https://www.egeda.ewg.apec.org/egeda/database_info/gas_monthly_select_form2.html and the data at the bottom of the page is used since it allows you to select all applicable data rather than data in small subsets.

    Parameters:
    - df (pd.DataFrame): The dataframe containing gas supply data.
    - ECONOMIES_TO_SPLIT_DICT (dict): A dictionary mapping economy codes to economy names. Currently, only OECD countries are considered as they are the ones for whom the esto data is not split into LNG and pipeline gas because it comes from the IEA.
    Returns:
    - df (pd.DataFrame): The modified dataframe with LNG and pipeline splits for relevant economies and years.
    """
    df_copy = df.copy()
    # Identify year columns
    year_columns = [col for col in df.columns if col.isdigit()]
    year_columns_to_modify = [col for col in year_columns if int(col) < OUTLOOK_BASE_YEAR]
    # breakpoint()
    # Filter data for OECD countries
    is_oecd_economy = df['economy'].isin(ECONOMIES_TO_SPLIT_DICT.keys())
    if not is_oecd_economy.any():
        # breakpoint()#why is sgp lng not included? what economies are we missing?
        # Filter for ECONOMIES_TO_SPLIT countries
        print('No OECD countries found in the dataset. Not modifying gas splits.')
        # breakpoint()
        return df
    df_oecd = df[is_oecd_economy].copy()
    #filter for only import and export rows where fuels is 08_gas
    df_oecd = df_oecd[(df_oecd['sectors'] == '02_imports') | (df_oecd['sectors'] == '03_exports')]
    df_oecd = df_oecd[df_oecd['fuels'] == '08_gas']
    #and where subfuels is 08_01_natural_gas 08_02_lng
    df_oecd = df_oecd[(df_oecd['subfuels'] == '08_01_natural_gas') | (df_oecd['subfuels'] == '08_02_lng')]

    # Process LNG and pipeline splits
    #check we can find the files:
    if not os.path.exists('../input_data/raw_data/gas_splits/esto_pipeline_imports.txt'):
        print('The gas splits files are missing. Not modifying gas splits.')
        breakpoint()
        return df
    pipeline_imports = pd.read_csv('../input_data/raw_data/gas_splits/esto_pipeline_imports.txt', delimiter="\t", skiprows=6)
    pipeline_exports = pd.read_csv('../input_data/raw_data/gas_splits/esto_pipeline_exports.txt', delimiter="\t", skiprows=6)
    lng_imports = pd.read_csv('../input_data/raw_data/gas_splits/esto_lng_imports.txt', delimiter="\t", skiprows=6)
    lng_exports = pd.read_csv('../input_data/raw_data/gas_splits/esto_lng_exports.txt', delimiter="\t", skiprows=6)
    # breakpoint()#why is sgp lng not included? what economies are we missing?
    # Filter for ECONOMIES_TO_SPLIT countries
    pipeline_imports = pipeline_imports[pipeline_imports['Member/Month'].isin(ECONOMIES_TO_SPLIT_DICT.values())]
    pipeline_exports = pipeline_exports[pipeline_exports['Member/Month'].isin(ECONOMIES_TO_SPLIT_DICT.values())]
    lng_imports = lng_imports[lng_imports['Member/Month'].isin(ECONOMIES_TO_SPLIT_DICT.values())]
    lng_exports = lng_exports[lng_exports['Member/Month'].isin(ECONOMIES_TO_SPLIT_DICT.values())]

    #map economy names to economy codes
    pipeline_imports.loc[:, 'Member/Month'] = pipeline_imports['Member/Month'].map({v: k for k, v in ECONOMIES_TO_SPLIT_DICT.items()})
    pipeline_exports.loc[:, 'Member/Month'] = pipeline_exports['Member/Month'].map({v: k for k, v in ECONOMIES_TO_SPLIT_DICT.items()})
    lng_imports.loc[:, 'Member/Month'] = lng_imports['Member/Month'].map({v: k for k, v in ECONOMIES_TO_SPLIT_DICT.items()})
    lng_exports.loc[:, 'Member/Month'] = lng_exports['Member/Month'].map({v: k for k, v in ECONOMIES_TO_SPLIT_DICT.items()})
    
    # Melt datasets to long format for easier processing
    pipeline_imports = pipeline_imports.melt(id_vars=['Member/Month'], var_name='Month', value_name='Pipeline Imports')
    pipeline_exports = pipeline_exports.melt(id_vars=['Member/Month'], var_name='Month', value_name='Pipeline Exports')
    lng_imports = lng_imports.melt(id_vars=['Member/Month'], var_name='Month', value_name='LNG Imports')
    lng_exports = lng_exports.melt(id_vars=['Member/Month'], var_name='Month', value_name='LNG Exports')

    # Merge datasets
    data = pipeline_imports.merge(pipeline_exports, on=['Member/Month', 'Month'], how='left')
    data = data.merge(lng_imports, on=['Member/Month', 'Month'], how='left')
    data = data.merge(lng_exports, on=['Member/Month', 'Month'], how='left')

    #in the Month col, extract only 4 digit years and make it an int
    data['Month'] = data['Month'].str.extract(r'(\d{4})')
    #now rename the cols
    data = data.rename(columns={'Member/Month': 'economy', 'Month': 'Year'})
    #melt the value cols
    
    #calcualte ratios of pipeline imports to lng imports and pipeline exports to lng exports
    data['Pipeline Imports'] = data['Pipeline Imports'].replace('-', 0).replace(np.nan, 0).astype(int)
    data['Pipeline Exports'] = data['Pipeline Exports'].replace('-', 0).replace(np.nan, 0).astype(int)
    data['LNG Imports'] = data['LNG Imports'].replace('-', 0).replace(np.nan, 0).astype(int)
    data['LNG Exports'] = data['LNG Exports'].replace('-', 0).replace(np.nan, 0).astype(int)
    
    #sum the values for the same economy and year and sector and subfuel
    data = data.groupby(['economy', 'Year']).sum().reset_index()
    # breakpoint()#where an economy has 0s for everything then we want to not do this one.
    if data[(data['Pipeline Imports'] != 0) & (data['Pipeline Exports'] != 0) & (data['LNG Imports'] != 0) & (data['LNG Exports'] != 0)].shape[0] == 0:
        print('No data found for LNG and pipeline imports/exports. Not modifying gas splits.')
        breakpoint()
        return df_copy
    data['Imports LNG Ratio'] = data.apply(lambda row: row['LNG Imports'] /(row['Pipeline Imports']+row['LNG Imports']) if (row['Pipeline Imports']+row['LNG Imports']) != 0 else 0, axis=1)
    data['Exports LNG Ratio'] = data.apply(lambda row: row['LNG Exports'] / (row['Pipeline Exports']+row['LNG Exports']) if (row['Pipeline Exports']+row['LNG Exports']) != 0 else 0, axis=1)
    #drop non ratios
    data = data.drop(columns=['Pipeline Imports', 'Pipeline Exports', 'LNG Imports', 'LNG Exports'])
    
    #if the economy is sealocked then we must assume everything is lngand also add on rpws for years all the way back to EBT_EARLIEST_YEAR (since we KNOW they would have been using lng) (for the other economies it is better to jsut leave the data as is to avoid estiamting anythign we dont know)
    SEALOCKED_ECONOMIES = ['08_JPN', '01_AUS', '12_NZ', '09_ROK', '15_PHL', '18_CT', '15_PHL']
    data['Imports LNG Ratio'] = data.apply(lambda row: 1 if row['economy'] in SEALOCKED_ECONOMIES else row['Imports LNG Ratio'], axis=1)
    data['Exports LNG Ratio'] = data.apply(lambda row: 1 if row['economy'] in SEALOCKED_ECONOMIES else row['Exports LNG Ratio'], axis=1)
    
    economy_data = df['economy'].unique()
    if data['economy'].isin(SEALOCKED_ECONOMIES).any():
        SEALOCKED_ECONOMIES = [e for e in SEALOCKED_ECONOMIES if e in economy_data]
        for year in range(OUTLOOK_BASE_YEAR+1, EBT_EARLIEST_YEAR-1, -1):
            year= str(year)
            for economy in SEALOCKED_ECONOMIES:
                if not data[(data['economy'] == economy) & (data['Year'] == year)].empty:
                    continue
                data = pd.concat([data, pd.DataFrame({'economy': economy, 'Year': year, 'Imports LNG Ratio': 1, 'Exports LNG Ratio': 1}, index=[0])])
    
    # Melt the data to long format
    data = data.melt(id_vars=['economy', 'Year'], var_name='sectors', value_name='Value')
    #where the sectors contains Imports set the sectors to 02_imports and where the sectors contains Exports set the sectors to 03_exports
    #then we will join on those cols to fill in all missing cols
    data['sectors'] = data['sectors'].apply(lambda x: '02_imports' if 'Imports' in x else '03_exports')
    #now we have the data in the correct format, we can merge it with the df_oecd
    #first melt the df_oecd
    df_oecd_melt = df_oecd.melt(id_vars=['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', 'subtotal_layout', 'subtotal_results'], var_name='Year', value_name='Value')
    # breakpoint()
    df_oecd_melt = df_oecd_melt[df_oecd_melt['Year'].astype(int) <= OUTLOOK_BASE_YEAR]
    #check there is no energy in the 08_02_lng subfuels
    if df_oecd_melt[(df_oecd_melt['fuels'] == '08_gas') & (df_oecd_melt['subfuels'] == '08_02_lng')]['Value'].sum() != 0:
        breakpoint()#i think we can just pass here since we have already split the data
        return df_copy
        # raise Exception(f'There is energy in the 08_02_lng subfuels for economy {df_oecd_melt["economy"].unique()}. Please check the data.')
    #drop the lng subfuels
    df_oecd_melt = df_oecd_melt[df_oecd_melt['subfuels'] != '08_02_lng']
    
    #adjust the names of the columns to match the data in df_oecd as well as work out what calcs to do
    # breakpoint()#can we save the ratio here so it can be used in EBT
    #save the ratio so it can be used in EBT for estiamting losses from lng prodcution:
    # breakpoint()
    data.to_csv('../output/output_data/lng_to_pipeline_trade_ratios.csv', index=False)
    #now merge
    df_oecd_melt = df_oecd_melt.merge(data, on=['economy', 'Year', 'sectors'], how='left', suffixes=('', '_lng_to_natgas_ratio'))
    
    #now calcualte the amount of lng energy and leave remaining as pipeline energy
    df_oecd_melt['LNG Supply'] = df_oecd_melt['Value'] * df_oecd_melt['Value_lng_to_natgas_ratio']
    df_oecd_melt['Value'] = df_oecd_melt['Value'] * (1 - df_oecd_melt['Value_lng_to_natgas_ratio'])
    
    #separrate the pipeline and lng supply
    df_oecd_melt = df_oecd_melt.drop(columns=['Value_lng_to_natgas_ratio'])
    lng_supply = df_oecd_melt.drop(columns=['Value']).rename(columns={'LNG Supply': 'Value'}).copy()
    pipeline_supply = df_oecd_melt.drop(columns=['LNG Supply']).copy()
    
    lng_supply['subfuels'] = '08_02_lng'
    
    #concat the two dataframes
    df_oecd_melt = pd.concat([pipeline_supply, lng_supply])
    #replace nas with 0
    df_oecd_melt['Value'] = df_oecd_melt['Value'].replace(np.nan, 0)
    #now we have the data in the correct format, we can merge it with the df_oecd
    #first melt the original df so we can merge it with the new data
    df = df.melt(id_vars=['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', 'subtotal_layout', 'subtotal_results'], var_name='Year', value_name='Value')
    #then do a outer merge on all cols
    new_data = df_oecd_melt.merge(df, on=['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', 'Year', 'subtotal_layout', 'subtotal_results'], how='outer', suffixes=('_new', ''))
    #where there is a value in the new data, replace the old value with the new value
    new_data['Value'] = np.where(new_data['Value_new'].notnull(), new_data['Value_new'], new_data['Value'])
    #drop the new value col
    new_data = new_data.drop(columns=['Value_new'])
    #check there are no duplicated rows
    if new_data.duplicated(subset=['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', 'Year', 'subtotal_layout', 'subtotal_results']).any():
        breakpoint()
        raise Exception('There are duplicated rows in the dataframe. Please check the data.')
    #now pivot out
    new_data_wide = new_data.pivot(index=['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', 'subtotal_layout', 'subtotal_results'], columns='Year', values='Value').reset_index()
    print(f'Imports and exports of gas have been split into LNG and pipeline gas for {economy_data}.')
    return new_data_wide

# Update the modify_dataframe_content function to use split_gas_splits_by_economy
def modify_gas_splits(df):
    """
    Modifies gas splits into LNG and pipeline for relevant economies and years.

    Parameters:
    - df (pd.DataFrame): The input dataframe.

    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    return split_gas_imports_exports_by_economy(df)

def ensure_all_year_cols_are_int(df):
    #in case manual edits are made to the data then make sure all data is int where we expect it. year cols are those with 4 digits
    year_columns = [col for col in df.columns if re.match(r'^\d{4}$', col)]
    # Coerce year columns to numeric, converting non-numeric values to NaN
    df_copy = df.copy()
    #set current nas to 123456789 so that we can spot new naas
    df_copy[year_columns] = df_copy[year_columns].replace(np.nan, 123456789)
    
    df_copy[year_columns] = df_copy[year_columns].apply(pd.to_numeric, errors='coerce')
    #if any nas then throw an error
    if df_copy[year_columns].isnull().any().any():
        na_cols   = []
        for col in year_columns:
            if df_copy[col].isnull().any():
                na_cols.append(col)
                print(f"NaN values found in column: {col}")
        breakpoint()#its confusing me how to extract exactly where these nas are.
        raise ValueError(f"There are NaN values in the year columns after coercion in columns: {na_cols}.")
    else:
        #set old nas, which would have been from missing values cause we dont have data for those years, back to na
        df_copy[year_columns] = df_copy[year_columns].replace(123456789, np.nan)
        
    return df_copy
def make_losses_and_own_use_bunkers_exports_positive(df):
    """
    Changes the numeric values in the year columns for rows where the 'losses_and_own_use_bunkers_exports' column
    is 'losses_and_own_use_bunkers_exports' from negative to positive.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    # Identifying year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Filtering rows where the 'sectors' column is losses_and_own_use_bunkers_exports
    condition = df['sectors'].isin(['04_international_marine_bunkers','05_international_aviation_bunkers', '10_losses_and_own_use', '03_exports'])
    # 04_international_marine_bunkers_positive, 05_international_aviation_bunkers_positive, 10_losses_and_own_use_positive, 03_exports_positive
    df_copy = df[condition].copy()
    # Change values from negative to positive for the identified rows and year columns
    df_copy.loc[condition, year_columns] = df_copy.loc[condition, year_columns].abs()
    df_copy['sectors'] = df_copy['sectors'] + '_positive'
    #also, we need to change the subsectors to have postive at end since the mappigns will sometimes use them. so wehre a sub1 sub2 and sub3 and su4sector is not x we need to change it to have positive at the end. This also prevents double counting when not expecting it
    df_copy['sub1sectors'] = df_copy['sub1sectors'].apply(lambda x: x+'_positive' if x != 'x' else x)
    df_copy['sub2sectors'] = df_copy['sub2sectors'].apply(lambda x: x+'_positive' if x != 'x' else x) 
    df_copy['sub3sectors'] = df_copy['sub3sectors'].apply(lambda x: x+'_positive' if x != 'x' else x)
    df_copy['sub4sectors'] = df_copy['sub4sectors'].apply(lambda x: x+'_positive' if x != 'x' else x)
    
    df = pd.concat([df, df_copy], ignore_index=True)
    
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

def copy_and_convert_imported_electricity_to_output_in_gwh(df):
    """
    Finds rows with specific criteria, copies them, modifies certain values including converting
    energy values from PJ to TWh, and appends the modified rows to the dataframe.

    The specific criteria are:
    - 'sectors' == '02_imports'
    - 'fuels' == '17_electricity'
    - 'sub1sectors' == 'x'

    The modifications for the copied rows are:
    - 'sectors' is changed to '18_electricity_output_in_gwh'
    - 'sub1sectors' is changed to 'x'
    - 'fuels' is changed to '22_imports'
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

def modify_hydrogen_green_electricity(df):
    """
    Searches for a row where it is '09_total_transformation_sector' in 'sectors',
    '09_13_hydrogen_transformation' in 'sub1sectors', '09_13_01_electrolysers' in 'sub2sectors' and '17_x_green_electricity' in 'fuels',
    and changes the 'sub1sectors' from '09_13_hydrogen_transformation' to '09_13x_hydrogen_transformation'.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    
    To be honest i dont know why we did create this ?
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
# def drop_hydrogen_transformation_rows(df):
#     """
#     Drops rows from the DataFrame where 'sub1sectors' is '09_13_hydrogen_transformation'.

#     Parameters:
#     - df (pd.DataFrame): The dataframe to modify.
    
#     Returns:
#     - df (pd.DataFrame): The modified dataframe with specified rows dropped.
#     """
#     # Define the condition for rows to drop
#     condition = df['sub1sectors'] == '09_13_hydrogen_transformation'
    
#     # Drop rows that match the condition
#     df = df[~condition]

#     return df

def create_net_emission_rows(df):
    #also want to create new lines for fuels == 23_total_combustion_emissions_net where their sectors now = 20_total_combustion_emissions
    #and then where sectors == 21_total_combustion_emissions_net,make thier fuels = 22_total_combustion_emissions
    condition = (df['sectors'] == '21_total_combustion_emissions_net') & (df['fuels'] == '23_total_combustion_emissions_net')
    new_rows1 = df[condition].copy()
    new_rows1['sectors'] = '20_total_combustion_emissions'
    new_rows2 = df[condition].copy()
    new_rows2['fuels'] = '22_total_combustion_emissions'
    # breakpoint()#why is net emisisons not correct for 'by sector'
    df = pd.concat([df, new_rows1, new_rows2], ignore_index=True)
    return df
    
def create_24_TPES_excluding_bunkers(df):
    #grab the tpes value and then minus the (negative) bunkers values from it so we have the tpes excluding bunkers
    tpes = df[df['sectors'] == '07_total_primary_energy_supply'].copy()
    bunkers = df[(df['sectors'] == '04_international_marine_bunkers') | (df['sectors'] == '05_international_aviation_bunkers')].copy()
    # Identify year columns (assuming columns are 4-digit years)
    year_columns = [col for col in df.columns if re.match(r'^\d{4}$', str(col))]
    historical_years = [str(year) for year in range(EBT_EARLIEST_YEAR, OUTLOOK_BASE_YEAR + 1)]
    max_year = max([int(year) for year in year_columns])
    future_years = [str(year) for year in range(OUTLOOK_BASE_YEAR + 1, max_year + 1)]
    # breakpoint()#is this right for the years
    # Merge the two dataframes on key columns to align TPES and bunkers
    key_cols = ['scenarios', 'economy','fuels', 'subfuels']#scenarios	economy	sectors	sub1sectors	sub2sectors	sub3sectors	sub4sectors	fuels	subfuels	subtotal_layout	subtotal_results

    tpes_historical = tpes[key_cols + ['subtotal_layout',  'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors'] + historical_years]
    tpes_future = tpes[key_cols + ['subtotal_results',  'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors'] + future_years]
    bunkers_historical = bunkers[key_cols + ['subtotal_layout'] + historical_years]
    bunkers_future = bunkers[key_cols + ['subtotal_results'] + future_years]
    # Set indexes for merging
    tpes_historical = tpes_historical.set_index(key_cols + ['subtotal_layout'])
    tpes_future = tpes_future.set_index(key_cols + ['subtotal_results'])
    bunkers_historical = bunkers_historical.set_index(key_cols + ['subtotal_layout'])
    bunkers_future = bunkers_future.set_index(key_cols + ['subtotal_results'])
    #sum up bunkers when we exclude its sectors cols so that we ahve aviation plus nabigation
    bunkers_historical = bunkers_historical.groupby(key_cols + ['subtotal_layout']).sum()
    bunkers_future = bunkers_future.groupby(key_cols + ['subtotal_results']).sum()
    
    
    # Merge historical and future dataframes with their respective bunkers
    tpes_historical_merged = tpes_historical.merge(
        bunkers_historical,
        left_index=True,
        right_index=True,
        how='left',
        suffixes=('', '_bunkers'),
        indicator=True
    )
    tpes_future_merged = tpes_future.merge(
        bunkers_future,
        left_index=True,
        right_index=True,
        how='left',
        suffixes=('', '_bunkers'),
        indicator=True
    )

    # Check for mismatches in merges (specifically, rightonly which is whre we have bunkers but no t TPES)
    if (tpes_historical_merged['_merge'] == 'right_only').any():
        mismatches = tpes_historical_merged[tpes_historical_merged['_merge'] == 'right_only']
        print("Mismatches found in historical merge:")
        print(mismatches)
        breakpoint()
        raise Exception("There are rows that do not match between historical TPES and bunkers data. Please check the data.")
    if (tpes_future_merged['_merge'] == 'right_only').any():
        #right_only means we have bunkers but no TPES so we need to check this
        mismatches = tpes_future_merged[tpes_future_merged['_merge'] == 'right_only']
        print("Mismatches found in future merge:")
        print(mismatches)
        breakpoint()
        raise Exception("There are rows that do not match between future TPES and bunkers data. Please check the data.")

    # Drop the merge indicator
    tpes_historical_merged = tpes_historical_merged.drop(columns=['_merge'])
    tpes_future_merged = tpes_future_merged.drop(columns=['_merge'])

    # For each year, subtract bunkers from TPES to get TPES excluding bunkers
    for year in historical_years:
        tpes_historical_merged[year] = tpes_historical_merged[year] - tpes_historical_merged[f"{year}_bunkers"].fillna(0)
    for year in future_years:
        tpes_future_merged[year] = tpes_future_merged[year] - tpes_future_merged[f"{year}_bunkers"].fillna(0)

    # Remove bunkers columns
    tpes_historical_merged = tpes_historical_merged[[col for col in tpes_historical_merged.columns if not col.endswith('_bunkers')]]
    tpes_future_merged = tpes_future_merged[[col for col in tpes_future_merged.columns if not col.endswith('_bunkers')]]

    # merge the historiacl and future dataframes back together
    tpes_new = pd.merge(
        tpes_historical_merged.reset_index(),
        tpes_future_merged.reset_index(),
        on=key_cols + ['sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors'],
        how='outer',
        suffixes=('_historical', '_future'),
        indicator=True
    )
    #double check fro indicators
    if (tpes_new['_merge'] != 'both').any():
        mismatches = tpes_new[tpes_new['_merge'] != 'both']
        print("Mismatches found in TPES excluding bunkers merge:")
        print(mismatches)
        breakpoint()
        raise Exception("There are rows that do not match between historical and future TPES excluding bunkers data. Please check the data.")
    # Reset index to return to original format
    tpes_new = tpes_new.reset_index(drop=True)
    
    tpes_new = tpes_new.drop(columns=['_merge'])
    # Set the correct labels for the new TPES excluding bunkers rows
    tpes_new['sectors'] = '24_TPES_excluding_bunkers'
    #check that the years look right. 
    # breakpoint()#
    # Concatenate the new rows to the original dataframe
    df_new = pd.concat([df, tpes_new], ignore_index=True)
    return df_new

def create_net_imports_rows(df):
    imports = df[df['sectors'] == '02_imports'].copy()
    exports = df[df['sectors'] == '03_exports'].copy()
    #join on key cols to calculate the net imports
    new_df = exports.merge(imports, on=['scenarios', 'economy', 'fuels', 'subfuels', 'subtotal_layout', 'subtotal_results'], how='outer', suffixes=('_export', '_import'))
    #extract year columns and then run through them calcualtiing the net imports
    year_columns = [col for col in df.columns if re.match(r'^\d{4}$', str(col))]
    # breakpoint()
    for col in year_columns:
        #add them together. if either is na though, set them to 0
        new_df[col] = new_df[col+'_import'].fillna(0) + new_df[col+'_export'].fillna(0)
    #drop the _import and _export cols
    new_df = new_df.drop(columns=[col for col in new_df.columns if '_import' in col or '_export' in col])
    #set sectors to 23_net_imports
    new_df['sectors'] = '23_net_imports'
    new_df['sub1sectors'] = 'x'
    new_df['sub2sectors'] = 'x'
    new_df['sub3sectors'] = 'x'
    new_df['sub4sectors'] = 'x'
    
    df = pd.concat([df, new_df], ignore_index=True)
    #check for duplicates
    if df.duplicated(subset=['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', 'subtotal_layout', 'subtotal_results']).any():
        breakpoint()
        raise Exception('There are duplicated rows in the dataframe. Please check the data.')
    return df

def rename_energy_df_where_ccs_in_subsectors_to_have_ccs_in_sector_and_fuels(df):
    """
    run through all the sub1, 2,3 4 sectors and chekc if _ccs is at the end of the name. if so then rename the sub1sectors name to have _ccs at the end.
    
    note that we pruposefully chose not to rename sectors col because it meant we would have to remap more things in the master_config.xlsx
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe.
    """
    df_copy = df.copy()
    for sector_col in ['sub2sectors', 'sub3sectors', 'sub4sectors']:
        other_cols = ['sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'subfuels', 'fuels']
        other_cols.remove(sector_col)
        # Define the condition for the rows to modify. make sure it avoids where str ends with _nonccs
        condition = df[sector_col].str.endswith('_ccs') & ~df[sector_col].str.endswith('_nonccs') & ~df[sector_col].str.endswith('wo_ccs')
        
        # Apply the modification to all other columns as long as _ccs is not there already, or they are x:
        for other_sector_col in other_cols:
            condition2 =  df[other_sector_col].str.endswith('_nonccs') |df[other_sector_col].str.endswith('_ccs') | (df[other_sector_col] == 'x') | df[other_sector_col].str.endswith('wo_ccs') 
            df.loc[condition & ~condition2, other_sector_col] = df.loc[condition & ~condition2, other_sector_col] + '_ccs'
    # breakpoint()#check it worked ok
    return df


# def rename_energy_df_where_ccs_in_sectors_to_have_ccs_in_fuel(df):
#     """
#     run through all the subfuels and chekc if _ccs is at the end of the name. if so then rename the fuels name to have _ccs at the end.
    
#     Parameters:
#     - df (pd.DataFrame): The dataframe to modify.
    
#     Returns:
#     - df (pd.DataFrame): The modified dataframe.
#     """
#     breakpoint()
#     for fuel_col in ['subfuels']:
#         # Define the condition for the rows to modify
#         condition = df[fuel_col].str.endswith('_ccs') & ~df[fuel_col].str.endswith('_nonccs') & ~df[fuel_col].str.endswith('wo_ccs')
#         if len(df.loc[condition, 'fuels']) > 0:
#             breakpoint()
#         # Apply the modification
#         df.loc[condition, 'fuels'] = df.loc[condition, 'fuels'] + '_ccs'

#     return df

def emissions_rename_sectors_and_negate_values_based_on_ccs_cap(df):
    """
    For rows with a suffix '_captured_emissions' in 'sub2sectors' or 'sub3sectors' columns:
    - Creates more rows and adds '_captured_emissions' to the suffix of the category name in the 'sectors' column and checks values in year columns are negative.
    #(redacted) - Copies these rows, renames the category in 'sectors' to '_captured_emissions_pos', and makes the year values positive.
    
    #note this got updated a little to make sure that there are never any duplicated sector names. i.e. previously we were jsut changeing sector names but allowing sub3/2/4/1sectors to have the same name as other ones.
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    
    Returns:
    - df (pd.DataFrame): The modified dataframe with additional rows appended.
    """
    # Identify year columns
    year_columns = [col for col in df.columns if col.isdigit()]

    # Define condition for rows to modify
    condition = df['sub2sectors'].str.endswith('_captured_emissions') | df['sub3sectors'].str.endswith('_captured_emissions')
    
    # Copy the rows that meet the condition, to modify and append them
    rows = df.loc[condition].copy()
    
    # Update 'sectors' and year values for rows matching the condition
    rows.loc[condition, 'sectors'] = rows.loc[condition, 'sectors'] + '_captured_emissions'
    
    # Update 'sectors' and year values for rows matching the condition
    rows.loc[condition, 'sub1sectors'] = rows.loc[condition, 'sub1sectors'] + '_captured_emissions'
    
    #where sub2sectors doesnt end with _captured_emissions then change that since we have to make sure that every sector is unique
    rows.loc[condition & ~rows['sub2sectors'].str.endswith('_captured_emissions'), 'sub2sectors'] += '_captured_emissions'
    
    #where sub3sectors is not x and doesnt end with _captured_emissions then change that since we have to make sure that every sector is unique
    rows.loc[condition & (rows['sub3sectors'] != 'x') & ~rows['sub3sectors'].str.endswith('_captured_emissions'), 'sub3sectors'] += '_captured_emissions'
    
    # breakpoint()#check above works
    for col in year_columns:
        #check if the values are negative, if not throw an error
        if (rows[col] > 0).any():
            raise Exception('There are positive values in the year columns for rows with "_captured_emissions" in "sub2sectors" or "sub3sectors".')
        
    #we also want these rows to be accessible within Total combustion emissions plotting name for fuels plotting aggregation. so copy the new rows and set the fuel to 22_total_combustion_emissions    
    new_rows = rows.copy()
    new_rows['fuels'] = '22_total_combustion_emissions'
    new_rows['subfuels'] = 'x'

    #we also want to be able to access these captrud emissions by fuel type. So we'll grab these rows, set their sectors to 20_total_combustion_emissions and their fuels to the fuels+captured_emissions
    new_fuels_rows = rows.copy()
    new_fuels_rows['sectors'] = '20_total_combustion_emissions'
    new_fuels_rows['sub1sectors'] = 'x'
    new_fuels_rows['sub2sectors'] = 'x'
    new_fuels_rows['sub3sectors'] = 'x'
    new_fuels_rows['sub4sectors'] = 'x'
    
    new_fuels_rows['fuels'] = new_fuels_rows['fuels'] + '_captured_emissions'   
    # breakpoint()#where are these values i cant find them
    # Copy the rows that meet the condition, to modify and append them
    # new_rows = rows.loc[condition].copy()
    # new_rows['sectors'] = new_rows['sectors'].str.replace('_captured_emissions', '_captured_emissions_pos')
    # for col in year_columns:
    #     new_rows[col] = new_rows[col].abs()  # Make values positive
    
    # # Copy new rows and rename the category in 'sectors' to '_emissions_area'
    # new_rows_area = new_rows.copy()
    # new_rows_area['sectors'] = new_rows_area['sectors'].str.replace('_emissions_captured_emissions_pos', '_emissions_area')

    # Concatenate the new rows to the original dataframe
    df = pd.concat([df, rows, new_rows, new_fuels_rows], ignore_index=True)
    #, new_rows, new_rows_area
    return df	
	

# def copy_and_modify_power_sector_rows(df):
#     """
#     Copies rows where 'sub1sectors' matches certain criteria and has negative values,
#     renames 'sectors' by adding '_net' to the end, turns the year values positive,
#     then appends them to the dataframe.
#     """
#     # Define the list of 'sub1sectors' values to filter
#     power_sectors = [
#         '09_01_electricity_plants',
#         '09_02_chp_plants',
#         '09_04_electric_boilers',
#         '09_05_chemical_heat_for_electricity_production',
#         '09_x_heat_plants'
#     ]

#     # Identify year columns
#     year_columns = [col for col in df.columns if col.isdigit()]

#     # Filter rows where 'sub1sectors' matches the criteria and has negative values in any year column
#     condition = (df['sectors'] == '09_total_transformation_sector') & df['sub1sectors'].isin(power_sectors) & (df[year_columns] < 0).any(axis=1)

#     # Filter rows matching the condition
#     filtered_rows = df[condition].copy()

#     # Modify 'sectors' by adding '_net' to the end
#     filtered_rows['sectors'] += '_net'

#     # Ensure all values in year columns are positive
#     filtered_rows[year_columns] = filtered_rows[year_columns].abs()

#     # Append the modified rows to the original dataframe
#     df = pd.concat([df, filtered_rows], ignore_index=True)

#     return df

def rename_production_16_others_x_to_16_others_unallocated(df):
    #because we have the possibility of having sectors='01_production' fuel=16_others, subfuels=x and subtotal=False,we need to rename the subfuels to 16_others_unallocated instead of x, so that the visualisation works as expected. We should also double check tnhere are no other instances like this for other sectors since we arent expecting htose (we'd jsut change this function to include them if we were - but its important to kniw it happens)
    # breakpoint()
    # Define the condition for the rows to modify
    condition = (df['fuels'] == '16_others') & \
                (df['subfuels'] == 'x') & \
                (df['subtotal_layout'] == False) & \
                (df['subtotal_results'] == False)

    #check that there are no other sectors that have 16_others and x as subfuels than 01_production
    max_year = max([int(year) for year in df.columns if re.match(r'^\d{4}$', str(year))])
    years = [str(year) for year in range(OUTLOOK_BASE_YEAR+1, max_year+1)]
    if df[(df['fuels'] == '16_others') & (df['subfuels'] == 'x') & (df['subtotal_layout'] == False) & (df['subtotal_results'] == False) & (df['sectors'] != '01_production')][years].sum().sum() != 0:
        breakpoint()
        # df.loc[condition, 'sub1sectors'] = '16_others_unallocated'
        raise Exception('There are sectors other than 01_production with 16_others and x as subfuels and subtotal=False. This function needs to be updated to include these sectors for subfuel 16_others_unallocated.')
    elif df[(df['fuels'] == '16_others') & (df['subfuels'] == 'x') & (df['subtotal_layout'] == False) & (df['subtotal_results'] == False) & (df['sectors'] == '01_production')][years].sum().sum() == 0:
        return df
    else:        
        # Apply the modification
        breakpoint()
        # df.loc[condition, 'sub1sectors'] = '16_others_unallocated'
        raise Exception('This function is not yet implemented. Please check for Temp fix for 01_production 15_solid_biomass and 16_others subtotal label within the EBT system, D_merging_results.py before running this function.')
    return df


def set_2013_thai_petroleum_refining_to_half_of_2012_2014(df):
    # find these rows and set 2013 to half of 2012 and 2014 because there is a really big jump in 2013 that seems unlikely (feel a bit uneasy about adjustung historcial data but for now we will try it and think on whether its a good idea or not. good to at least do it once!):
    #sectors: 12_total_final_consumption 17_nonenergy_use, 09_total_transformation_sector > 09_07_oil_refineries
    #fuels: 07_petroleum_products	07_x_other_petroleum_products
    #is_subtotal: FALSE
    #years :2012	2013	2014
    #
    #         economy	sectors	sub1sectors	sub2sectors	sub3sectors	sub4sectors	fuels	subfuels
    #         19_THA	09_total_transformation_sector	09_07_oil_refineries	x	x	x	07_petroleum_products	07_x_other_petroleum_products
    # 19_THA	12_total_final_consumption	x	x	x	x	07_petroleum_products	07_x_other_petroleum_products
    # 19_THA	17_nonenergy_use	x	x	x	x	07_petroleum_products	07_x_other_petroleum_products
    maps = [('19_THA', '09_total_transformation_sector', '09_07_oil_refineries', 'x', 'x', 'x', '07_petroleum_products', '07_x_other_petroleum_products'),
            ('19_THA', '12_total_final_consumption', 'x', 'x', 'x', 'x', '07_petroleum_products', '07_x_other_petroleum_products'),
            ('19_THA', '17_nonenergy_use', 'x', 'x', 'x', 'x', '07_petroleum_products', '07_x_other_petroleum_products')]
    for scenario in df['scenarios'].unique():
        for map in maps:
            # breakpoint()#still havent 2x checked this works
            economy, sectors, sub1sectors, sub2sectors, sub3sectors, sub4sectors, fuels, subfuels = map
            year1 = 2012
            year2 = 2013
            year3 = 2014
            #find and check they are only 1 row for each scenario
            row = df.loc[(df['economy'] == economy) & (df['sectors'] == sectors) & (df['sub1sectors'] == sub1sectors) & (df['sub2sectors'] == sub2sectors) & (df['sub3sectors'] == sub3sectors) & (df['sub4sectors'] == sub4sectors) & (df['fuels'] == fuels) & (df['subfuels'] == subfuels) & (df['scenarios'] == scenario)]
            if row.shape[0] != 1:
                raise Exception(f'There are {row.shape[0]} rows for the economy {economy}, sectors {sectors}, sub1sectors {sub1sectors}, sub2sectors {sub2sectors}, sub3sectors {sub3sectors}, sub4sectors {sub4sectors}, fuels {fuels}, subfuels {subfuels}, scenario {scenario}. We think there should only be 1 row.')
            # breakpoint()
            value1 = row[str(year1)].values[0]
            value2 = row[str(year2)].values[0]
            value3 = row[str(year3)].values[0]
            #set the value of 2013 to half of 2012 and 2014
            # breakpoint()
            df.loc[(df['economy'] == economy) & (df['sectors'] == sectors) & (df['sub1sectors'] == sub1sectors) & (df['sub2sectors'] == sub2sectors) & (df['sub3sectors'] == sub3sectors) & (df['sub4sectors'] == sub4sectors) & (df['fuels'] == fuels) & (df['subfuels'] == subfuels) & (df['scenarios'] == scenario), str(year2)] = (value1 + value3) / 2
            breakpoint()#save these cahnges elsewhere
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
