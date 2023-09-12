
#import data from input_data/model_df_wide_20230420.csv. This is the data from the concatenation of all data for the 9th edition modelling (created in https://github.com/asia-pacific-energy-research-centre/Outlook9th_EBT). 
#this data is used to create the data that is used in the charts, which is saved in intermediate_data/data/data_mapped_to_plotting_names_9th.pkl
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
STRICT_DATA_CHECKING = False
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)
        
import mapping_functions

#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')
RAISE_ERROR = False
#%%
#read in data in either Excel or CSV file format
import glob

file_pattern = '../input_data/*.*'
file_paths = glob.glob(file_pattern)

if len(file_paths) == 0:
    print("No matching file found.")
else:
    file_path = file_paths[0]
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        model_df_wide = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        model_df_wide = pd.read_csv(file_path)
    else:
        print("Unsupported file format.")

#%%
##############################################################################

#import mappings:
#these will be mappings from the names used to refer to categories shown in the plotting, to the combinations of column categories from which these categories are aggregated from.
# Eg: Buildings is extracted by finding all values with 16_01_buildings in their sub1sectors column. Also Bunkers is extacted by finding all values with 04_international_marine_bunkers or 05_international_aviation_bunkers in their sectors column
#The mappings are used to reduce dataframe manipulations, as a lot of code is needed to manually extract the categories from the columns when they come from so many different columns and combinations. 

sector_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='sectors_plotting')
# sector_plotting_mappings.columns Index(['sectors_plotting', 'sectors', 'sub1sectors', 'sub2sectors'], dtype='object')

fuel_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='fuels_plotting')
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
#%%
##############################################################################
#########################

#BEGIN PROCESSING THE DATA

#############################
#FORMAT THE MAPPINGS
#for fuel and sector mappings we will extract the most sepcific reference for each row and then record it's column in a column called 'column'.
#so for example, where we want to extract the reference for the sectors_plotting value Agriculture, we find the rightmost column that is not na (this is the msot specific column), set 'reference_sector' to that value in the most specific column, and then the column to the name of the most specific column

new_sector_plotting_mappings, new_fuel_plotting_mappings = mapping_functions.format_plotting_mappings(sector_plotting_mappings, fuel_plotting_mappings)

new_charts_mapping = mapping_functions.format_charts_mapping(charts_mapping)
mapping_functions.save_plotting_names_order(charts_mapping,FILE_DATE_ID)

#CHECKING
#check that there are no plotting names that are duplcaited between fuels and sectors:
plotting_names = mapping_functions.check_for_duplicates_in_plotting_names(new_sector_plotting_mappings, new_fuel_plotting_mappings, RAISE_ERROR=RAISE_ERROR)
mapping_functions.test_charts_mapping(new_charts_mapping)
mapping_functions.test_plotting_names_match_charts_mapping(plotting_names,new_charts_mapping)  
mapping_functions.test_plotting_names_match_colors_df(plotting_names,colors_df)
#CHECKING OVER
#%%
#############################
#PROCESS THE DATA
#############################

#because we have issues with data being too large (mappings can possibly increase size of data too), we will run through each eocnomy in the model_df_wide and save it as a pickle separately.
for economy_x in model_df_wide['economy'].unique():
    model_df_wide_economy = model_df_wide[model_df_wide['economy'] == economy_x]

    
    #make model_df_wide_economy into model_df_tall
    #fgirst grab object copls as the index cols
    index_cols = model_df_wide_economy.select_dtypes(include=['object']).columns
    #now melt the data
    model_df_tall = pd.melt(model_df_wide_economy, id_vars=index_cols, var_name='year', value_name='value')
    

    #data details:
    #Columns: model_df_wide_economy.columns
    # Index(['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors',
    #        'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', '1980', '1981',
    #        '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990',...................
    #        '2063', '2064', '2065', '2066', '2067', '2068', '2069', '2070'],
    #       dtype='object')

    ##############################################################################

    #print column types for all columns
    # for col in model_df_wide_economy.columns:
    #     print(col, model_df_wide_economy[col].dtype)
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
    
    mapping_functions.check_data_matches_expectations(model_df_wide_economy, model_variables, RAISE_ERROR=False)
    
    #############################
    #EXTRACT PLOTTING NAMES FROM MODEL DATA
    #and now these mappings can be joined to the model_df and used to extract the data needed for each plotting_name. it will create a df with only the fuel or sectors columns: fuels_plotting and sectors_plotting, which contains defintiions of all the possible combinations of fuels_plotting and sectors_plotting we could have.. i think.

    model_df_tall_sectors = mapping_functions.merge_sector_mappings(model_df_tall, new_sector_plotting_mappings,sector_plotting_mappings, RAISE_ERROR=RAISE_ERROR)
        
    model_df_tall_sectors_fuels = mapping_functions.merge_fuel_mappings(model_df_tall_sectors, new_fuel_plotting_mappings,fuel_plotting_mappings, RAISE_ERROR=RAISE_ERROR)

    #call it plotting_df
    plotting_df = model_df_tall_sectors_fuels.copy()
    #############################
    #TRANSFORMATION MAPPING
    #next step will include creating new datasets which create aggregations of data to match some of the categories plotted in the 8th edition. 
    #for example we need an aggregation of the transformation sector input and output values to create entries for Power, Refining or Hydrogen

    input_transformation, output_transformation = mapping_functions.merge_transformation_sector_mappings(model_df_tall, transformation_sector_mappings,new_fuel_plotting_mappings,RAISE_ERROR=RAISE_ERROR)
    
    #Thats it. We will stack this with the other dataframes later on. 
    plotting_df = pd.concat([plotting_df, input_transformation, output_transformation])
    
    #drop all cols excet ['scenarios','economy', 'year','value','fuels_plotting', 'sectors_plotting']
    plotting_df= plotting_df[['scenarios','economy', 'year','value','fuels_plotting', 'sectors_plotting']]
    #now join with charts mapping on fuel and sector plotting names to get the plotting names for the transformation sectors
    economy_new_charts_mapping = new_charts_mapping.merge(plotting_df, how='left', on=['fuels_plotting', 'sectors_plotting'])
    

    economy_new_charts_mapping = economy_new_charts_mapping.groupby(['economy','table_number','sheet_name', 'chart_type', 'sectors_plotting', 'fuels_plotting', 'plotting_column', 'aggregate_column', 'scenarios', 'year', 'table_id']).sum().reset_index()
    breakpoint()
    #############################
    #now we can extract the data for each graph we need to produce (as stated in the charts_mapping)
    
    #for each unique sheet, table combination in new_charts_mapping, extract the values from the cols plotting names cols which specifies the data we need to grab from the new plotting_df. Note that this doesnt define whether the plotting name is from secotrs or fuels, but as long as the plotting names are unique it shouldnt matter (which they should be)
    
    missing_data = economy_new_charts_mapping[economy_new_charts_mapping['value'].isnull()]
    economy_new_charts_mapping = economy_new_charts_mapping.dropna(subset=['value'])
    
    #TEST WE COULD DELETE
    #now we have a dataframe called missing_data which contains the data we dont have mapped, yet. This shouldnt happen and i think i dont need this code. but i will leave it here for now just in case.
    if len(missing_data) > 0:
        data_checking_warning_or_error(('There are ' + str(len(missing_data)) + ' missing values in the plotting_df. These are for: ', missing_data[['table_id']].drop_duplicates()))
    else:
        print('There are no missing values in the plotting_df')

    
    #check for duplicates. not sure why there are duplicates, but there are. so drop them
    #I DONT THINK THESE ARE AN ISSUE, THEY JUST NEED TO BE SUMMED UP?
    if len(economy_new_charts_mapping[economy_new_charts_mapping.duplicated()]) > 0:
        print('There are ' + str(len(economy_new_charts_mapping[economy_new_charts_mapping.duplicated()])) + ' duplicates in the economy_new_charts_mapping dataframe')
        economy_new_charts_mapping = economy_new_charts_mapping.drop_duplicates()
    else:
        print('There are no duplicates in the economy_new_charts_mapping dataframe')
    
    #TEST WE COULD DELETE over
    #TEMP:
    #set unit to 'Petajoules'. for now we dont have any other units so can set it here but may have to change this later, depending on how we deal with that new data (eg activity data.)
    economy_new_charts_mapping['unit'] = 'Petajoules'
    #rename scenarios to scenario
    economy_new_charts_mapping.rename(columns={'scenarios':'scenario'}, inplace=True)
    #############################
    #save data to pickle
    #and sav economy_new_charts_mapping to pickle since its useful
    economy_new_charts_mapping.to_pickle(f'../intermediate_data/data/economy_charts_mapping_9th_{economy_x}_{FILE_DATE_ID}.pkl')

#%%
#economy_new_charts_mapping= pd.read_pickle(f'../intermediate_data/data/economy_charts_mapping_9th_19_THA_20230725.pkl')

