
#import data from input_data/model_df_wide_20230420.csv. This is the data from the concatenation of all data for the 9th edition modelling (created in https://github.com/asia-pacific-energy-research-centre/Outlook9th_EBT). 
#this data is used to create the data that is used in the charts, which is saved in intermediate_data/data/data_mapped_to_plotting_names_9th.pkl
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys
import glob
import re
STRICT_DATA_CHECKING = False
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)
        
import mapping_functions
      

def map_9th_data_to_plotting_template_handler(FILE_DATE_ID, ECONOMY_ID, RAISE_ERROR=False, sources = ['energy', 'capacity', 'emissions']):
    """Maps the 9th edition data to the plotting template. Many of the functions in this file are from mapping_functions.py

    Args:
        FILE_DATE_ID (str): Identifier for the date on which the file was generated. 
                            Used to version control the output and mapping files.
                            
        ECONOMY_ID (str): Unique identifier for the economy being analyzed. 
                          Used to filter input data and to name output files.
                          
        RAISE_ERROR (bool, optional): Flag to indicate whether to raise exceptions or warnings during execution. 
                                      If set to True, the function will halt on encountering any inconsistencies. 
                                      Defaults to False.
                                      
               
    Raises:
        Exception: If no files are found or if multiple files are found for a single economy when USE_ECONOMY_ID is True.
        
    Notes:
        - The function uses various auxiliary mappings stored in Excel sheets for data transformation.
        - DataFrames are manipulated in wide and tall formats for ease of computation.
        - Validation checks are done to ensure data integrity and schema conformity.
    """
    
    def find_and_load_latest_data_for_all_sources(ECONOMY_ID, sources):
        # Initialize variables
        all_file_paths = []
        all_model_df_wides = []
        folder =f'../input_data/{ECONOMY_ID}/'
        all_model_df_wides_dict = {}
        # Fetch file paths based on the configuration
    
        for root, dirs, files in os.walk(folder):
            all_file_paths.extend(glob.glob(os.path.join(root, "*.*")))

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
            all_model_df_wides_dict[source] = file_path
            if file_path is None:
                print(f'No latest date id was idenitfied for {source} files')
            
        # Check if there are any files_missing_source
        files_missing_source = [file_path for file_path in all_file_paths if file_path not in all_files_with_source]
        if len(files_missing_source) > 0:
            print(f'The following files were not identified as an energy, capacity or emissions file: {files_missing_source}')
        
        def load_data_to_df(file_path, df_list):
            if file_path.endswith(('.xlsx', '.xls')):
                df_list.append(pd.read_excel(file_path))
            elif file_path.endswith('.csv'):
                df_list.append(pd.read_csv(file_path))
            else:
                breakpoint()
                raise Exception(f"Unsupported file format for {file_path}")

        # Load data into DataFrames and
        for source in all_model_df_wides_dict.keys():
            file_path = all_model_df_wides_dict[source]
            load_data_to_df(file_path, all_model_df_wides_dict[source])
            
        return all_model_df_wides_dict
    
    all_model_df_wides_dict = find_and_load_latest_data_for_all_sources(ECONOMY_ID, sources)
            
    ##############################################################################

    #import mappings:
    #these will be mappings from the names used to refer to categories shown in the plotting, to the combinations of column categories from which these categories are aggregated from.
    # Eg: Buildings is extracted by finding all values with 16_01_buildings in their sub1sectors column. Also Bunkers is extacted by finding all values with 04_international_marine_bunkers or 05_international_aviation_bunkers in their sectors column
    #The mappings are used to reduce dataframe manipulations, as a lot of code is needed to manually extract the categories from the columns when they come from so many different columns and combinations. 

    sector_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='sectors_plotting')
    # sector_plotting_mappings.columns Index(['sectors_plotting', 'sectors', 'sub1sectors', 'sub2sectors'], dtype='object')

    fuel_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='fuels_plotting')
    
    capacity_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='capacity_plotting')
    
    emissions_fuel_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='emissions_fuel_plotting')
    
    emissions_sector_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='emissions_sector_plotting')
    # fuel_plotting_mappings.columns Index(['fuels_plotting', 'fuels', 'subfuels'], dtype='object')

    transformation_sector_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='transformation_sector_mappings')
    # transformation_sector_mappings.columns: input_fuel	transformation_sectors	sub1sectors

    charts_mapping = pd.read_excel('../config/master_config.xlsx', sheet_name='table_id_to_chart', header = 1)

    colors_df = pd.read_excel('../config/master_config.xlsx', sheet_name='colors')

    #also plot a color wheel for the user to understand the colors_df
    #NOTE THAT I DIDNT GET AROUND TO MAKING THIS WORK SORRY
    # mapping_functions.prepare_color_plot(colors_df)
    #just need to double check all plotting names are in here
    ##############################################################################

    #take in the 9th_EBT_schema file. This will be used to check that the unique variables in the columns in Variables sheet match the variables in the columns in the Data sheet (model_df_wide). If not, throw a descriptive error/warning.

    model_variables = pd.read_excel('../config/9th_EBT_schema.xlsx', header = 2)

    ##############################################################################
    #########################

    #BEGIN PROCESSING THE DATA

    #############################
    #FORMAT THE MAPPINGS
    #for fuel and sector mappings we will extract the most sepcific reference for each row and then record it's column in a column called 'column'.
    #so for example, where we want to extract the reference for the sectors_plotting value Agriculture, we find the rightmost column that is not na (this is the msot specific column), set 'reference_sector' to that value in the most specific column, and then the column to the name of the most specific column
    all_plotting_mapping_dicts = {'sector_energy': {'df': sector_plotting_mappings, 
                                       'columns': ['sub2sectors', 'sub1sectors', 'sectors'],
                                       'source': 'energy',
                                       'plotting_name_column': 'sectors_plotting'},
                            'fuel_energy': {'df': fuel_plotting_mappings,
                                        'columns': ['subfuels', 'fuels'],
                                        'source': 'energy',
                                        'plotting_name_column': 'fuels_plotting'},
                            'emissions_sector': {'df': emissions_sector_plotting_mappings,
                                        'columns': ['fuels', 'subfuels'],
                                        'source': 'emissions',
                                        'plotting_name_column': 'emissions_sector_plotting'},
                            'emissions_fuel': {'df': emissions_fuel_plotting_mappings,
                                        'columns': ['fuels', 'subfuels'],
                                        'source': 'emissions',
                                        'plotting_name_column': 'emissions_fuel_plotting'},
                            'capacity': {'df': capacity_plotting_mappings,
                                        'columns': ['sub2sectors', 'sub1sectors', 'sectors'],
                                        'source': 'capacity',
                                        'plotting_name_column': 'capacity_plotting'}
                            }    
    plotting_names = []
    for plotting_mapping in all_plotting_mapping_dicts.keys():
        plotting_mapping_dict = all_plotting_mapping_dicts[plotting_mapping]
        columns =  plotting_mapping_dict['columns']
        df = plotting_mapping_dict['df']
        source = plotting_mapping_dict['source']
        plotting_name_column = plotting_mapping_dict['plotting_name_column']
        df = mapping_functions.format_plotting_mappings(df, columns, source, plotting_name_column)
        all_plotting_mapping_dicts[plotting_mapping]['df'] = df
        plotting_names = plotting_names + df['plotting_name'].unique().tolist() 
        
    plotting_names = set(plotting_names)
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict = {}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['energy'] = {'sectors_plotting':'fuels_plotting', 'fuels_plotting':'sectors_plotting'}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['capacity'] = {'capacity_plotting':'capacity_plotting'}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['emissions'] = {'emissions_sector_plotting':'emissions_fuel_plotting', 'emissions_fuel_plotting':'emissions_sector_plotting'}
    
    new_charts_mapping = mapping_functions.format_charts_mapping(charts_mapping, source_and_aggregate_name_column_to_plotting_name_column_mapping_dict)
    mapping_functions.save_plotting_names_order(charts_mapping,FILE_DATE_ID)
    #new_sector_plotting_mappings['sectors_plotting'].unique().tolist() + new_fuel_plotting_mappings['fuels_plotting'].unique().tolist())
    #CHECKING
    #check that there are no plotting names that are duplcaited between fuels and sectors:
    # plotting_names = mapping_functions.check_for_duplicates_in_plotting_names(new_sector_plotting_mappings, new_fuel_plotting_mappings, RAISE_ERROR=RAISE_ERROR)
    mapping_functions.test_charts_mapping(new_charts_mapping)
    mapping_functions.test_plotting_names_match_charts_mapping(plotting_names,new_charts_mapping)  
    mapping_functions.test_plotting_names_match_colors_df(plotting_names,colors_df)
    #CHECKING OVER

    #############################
    #PROCESS THE DATA
    #############################
    
    for source in all_model_df_wides_dict.keys():
        filename = all_model_df_wides_dict[source][0]
        model_df_wide = all_model_df_wides_dict[source][1]
        #because we have issues with data being too large (mappings can possibly increase size of data too), we will run through each eocnomy in the model_df_wide and save it as a pickle separately.
        # for economy_x in model_df_wide['economy'].unique():
        #     model_df_wide_economy = model_df_wide[model_df_wide['economy'] == economy_x]
        
        #check if the data is for energy, capacity or emissions by checking the name of the file (if it contains energy, capacity or emissions in the filename)
        
        #NOTE THAT WE ARE ASSUMING THAT EACH MODEL DF WILL ONLY CONTAIN ONE ECONOMY. THIS IS TRUE FOR THE 9TH EDITION BUT MAY NOT BE TRUE FOR FUTURE EDITIONS
        economy_x = model_df_wide['economy'].unique()[0]
        model_df_wide['source'] = source
        #make model_df_wide_economy into model_df_tall
        #fgirst grab object copls as the index cols
        index_cols = model_df_wide.select_dtypes(include=['object', 'bool']).columns
        #now melt the data
        model_df_tall = pd.melt(model_df_wide, id_vars=index_cols, var_name='year', value_name='value')
        # Convert year to int
        model_df_tall['year'] = model_df_tall['year'].astype(int)

        # Filter to only take the lowest level values. these differ based on if the data was based on the ESTO data file or actually projected data (since the projections are based on what sectors/fuels the modellers wanted to model, which can be more or less detailed than the ESTO data)
        # model_df_tall = model_df_tall[((model_df_tall['year'] <= 2020) & (model_df_tall['subtotal_layout'] == False)) | ((model_df_tall['year'] > 2020) & (model_df_tall['subtotal_results'] == False))]
        #drop where either subtotal_layout or subtotal_results is true
        model_df_tall = model_df_tall[(model_df_tall['subtotal_layout'] == False) & (model_df_tall['subtotal_results'] == False)]

        # Dropping unnecessary columns
        model_df_tall = model_df_tall.drop(columns=['subtotal_layout', 'subtotal_results'])

        #data details:
        #Columns: model_df_wide.columns
        # Index(['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors',
        #        'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', '1980', '1981',
        #        '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990',...................
        #        '2063', '2064', '2065', '2066', '2067', '2068', '2069', '2070'],
        #       dtype='object')

        ##############################################################################

        #print column types for all columns
        # for col in model_df_wide.columns:
        #     print(col, model_df_wide[col].dtype)
        # scenarios object
        # economy object
        # sectors object
        # sub1sectors object
        # sub2sectors object
        # sub3sectors object
        # sub4sectors object
        # fuels object
        # subfuels object
        # 1980 float64


        ##############################################################################
        
        mapping_functions.check_data_matches_expectations(model_df_wide, model_variables, RAISE_ERROR=False)
        
        #############################
        #EXTRACT PLOTTING NAMES FROM MODEL DATA
        #and now these mappings can be joined to the model_df and used to extract the data needed for each plotting_name. it will create a df with only the fuel or sectors columns: fuels_plotting and sectors_plotting, which contains defintiions of all the possible combinations of fuels_plotting and sectors_plotting we could have.. i think.
        if source.isin(['energy', 'emissions']):
            #energy and emissions are mapped to both sector and fuel columns so we needed to identify the most specific sector and fuel columns for each row and then join on them. this requires two processes below:
            new_sector_plotting_mappings = all_plotting_mapping_dicts['sector'+'_'+source]['df']
            model_df_tall_sectors = mapping_functions.merge_sector_mappings(model_df_tall, new_sector_plotting_mappings,sector_plotting_mappings, source, RAISE_ERROR=RAISE_ERROR)
            breakpoint()
            
            new_fuel_plotting_mappings = all_plotting_mapping_dicts['fuel'+'_'+source]['df']
            model_df_tall_sectors_fuels = mapping_functions.merge_fuel_mappings(model_df_tall_sectors, new_fuel_plotting_mappings,fuel_plotting_mappings, source, RAISE_ERROR=RAISE_ERROR)#losing access to 19_total because of filtering for lowest level values. not sure how to avoid
            # model_df_tall = model_df_tall_sectors_fuels.copy()
            breakpoint()
        elif source == 'capacity':
            #capacity is just based off sectors so its relatively simple
            new_capacity_plotting_mappings = all_plotting_mapping_dicts['capacity']['df']
            model_df_tall_capacity = mapping_functions.merge_capacity_mappings(model_df_tall, new_capacity_plotting_mappings,capacity_plotting_mappings, source, RAISE_ERROR=RAISE_ERROR)
            breakpoint()
            # model_df_tall = model_df_tall_capacity.copy()
        
        # new_emissions_plotting_mappings = all_plotting_mapping_dicts['emissions']['df']
        # model_df_tall_emissions = mapping_functions.merge_emissions_mappings(model_df_tall, new_emissions_plotting_mappings,emissions_plotting_mappings, RAISE_ERROR=RAISE_ERROR)
        # breakpoint()
        
        # #call it plotting_df
        # plotting_df = model_df_tall_sectors_fuels.copy()
        #############################
        #TRANSFORMATION MAPPING
        #next step will include creating new datasets which create aggregations of data to match some of the categories plotted in the 8th edition. 
        #for example we need an aggregation of the transformation sector input and output values to create entries for Power, Refining or Hydrogen
        # breakpoint()#we get nas in the transformation sector mappings. why??
        if source.isin(['energy']):
            input_transformation, output_transformation = mapping_functions.merge_transformation_sector_mappings(model_df_tall, transformation_sector_mappings,new_fuel_plotting_mappings,RAISE_ERROR=RAISE_ERROR)
            #concat all the dataframes together?
            plotting_df = pd.concat([model_df_tall_sectors_fuels, input_transformation, output_transformation])
        elif source == 'capacity':
            plotting_df = model_df_tall_capacity.copy()
        elif source == 'emissions':
            plotting_df = model_df_tall_sectors_fuels.copy()
        else:
            breakpoint()
            raise Exception('source is not valid')  
        
        # #identify where fuels_plotting is Solar and year is 2003:
        # input_transformation.loc[(input_transformation.fuels_plotting == 'Solar') & (input_transformation.year == 2003)]
        # #look for wehre subfuels is 12_01_of_which_photovoltaics and year is 2003
        # model_df_tall.loc[(model_df_tall.subfuels == '12_01_of_which_photovoltaics') & (model_df_tall.year == 2003)]
        
        #Thats it. We will stack this with the other dataframes later on. 
        # plotting_df = pd.concat([plotting_df, input_transformation, output_transformation])
        
        #drop all cols excet ['scenarios','economy', 'year','value','fuels_plotting', 'sectors_plotting']
        # plotting_df= plotting_df[['scenarios','economy', 'year','value','fuels_plotting', 'sectors_plotting']]
        # plotting_df = plotting_df[['scenarios','economy', 'year','value','aggregate_name_column', 'aggregate_name', 'plotting_name_column', 'plotting_name']]#is this right? should plotting name not be something different, it seems to be the same as aggregate name. should it not be reference name or reference column
        #now join with charts mapping on fuel and sector plotting names to get the plotting names for the transformation sectors
        economy_new_charts_mapping = new_charts_mapping.merge(plotting_df, how='left', on=['aggregate_name_column', 'aggregate_name', 'plotting_name_column', 'plotting_name']) #is this gonna be right
        
        economy_new_charts_mapping = economy_new_charts_mapping.groupby(['source', 'economy','table_number','sheet_name', 'chart_type', 'plotting_name_column', 'plotting_name','aggregate_name_column', 'aggregate_name', 'scenarios', 'year', 'table_id']).sum().reset_index()
        
        #############################
        #now we can extract the data for each graph we need to produce (as stated in the charts_mapping)
        
        #for each unique sheet, table combination in new_charts_mapping, extract the values from the cols plotting names cols which specifies the data we need to grab from the new plotting_df. Note that this doesnt define whether the plotting name is from secotrs or fuels, but as long as the plotting names are unique it shouldnt matter (which they should be)
        
        missing_data = economy_new_charts_mapping[economy_new_charts_mapping['value'].isna()]
        economy_new_charts_mapping = economy_new_charts_mapping.dropna(subset=['value'])
        
        #TEST WE COULD DELETE
        #now we have a dataframe called missing_data which contains the data we dont have mapped, yet. This shouldnt happen and i think i dont need this code. but i will leave it here for now just in case.
        if len(missing_data) > 0:
            data_checking_warning_or_error(f'There are {str(len(missing_data))} missing values in the plotting_df for {source}. These are for: {missing_data[["table_id"]].drop_duplicates()}')
        
        #check for duplicates. not sure why there are duplicates, but there are. so drop them
        #I DONT THINK THESE ARE AN ISSUE, THEY JUST NEED TO BE SUMMED UP?
        if len(economy_new_charts_mapping[economy_new_charts_mapping.duplicated()]) > 0:
            print('There are ' + str(len(economy_new_charts_mapping[economy_new_charts_mapping.duplicated()])) + ' duplicates in the economy_new_charts_mapping dataframe for ' + source)
            economy_new_charts_mapping = economy_new_charts_mapping.drop_duplicates()
        
        #TEST WE COULD DELETE over
        #TEMP:
        #set unit to 'Petajoules'. for now we dont have any other units so can set it here but may have to change this later, depending on how we deal with that new data (eg activity data.)
        unit_dict = {'energy': 'Petajoules', 'capacity': 'GW', 'emissions': 'MtCO2e'}
        economy_new_charts_mapping['unit'] = economy_new_charts_mapping['source'].map(unit_dict)
        #rename scenarios to scenario
        economy_new_charts_mapping.rename(columns={'scenarios':'scenario'}, inplace=True)
        #set the year column to int
        economy_new_charts_mapping.year = economy_new_charts_mapping.year.astype(int)
        #############################
        # Save the processed data to a pickle file
        economy_new_charts_mapping.to_pickle(f'../intermediate_data/data/charts_mapping_{source}_{economy_x}_{FILE_DATE_ID}.pkl')
        print(f"Data for {economy_x} {source} saved.")

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
#%%
FILE_DATE_ID = '20231110'
ECONOMY_ID = '19_THA'
map_9th_data_to_plotting_template_handler(FILE_DATE_ID, ECONOMY_ID, RAISE_ERROR=False, USE_ECONOMY_ID=True)
#%%