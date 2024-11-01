
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
from utility_functions import *
STRICT_DATA_CHECKING = False
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)
        
import mapping_functions
      

def map_9th_data_to_two_dimensional_plots(FILE_DATE_ID, ECONOMY_ID, EXPECTED_COLS, RAISE_ERROR=False, sources = ['energy', 'capacity', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2']):
    """Maps the 9th edition data to the plotting template for 2d plots. Many of the functions in this file are from mapping_functions.py

    Args:
        FILE_DATE_ID (str): Identifier for the date on which the file was generated. 
                            Used to version control the output and mapping files.
                            
        ECONOMY_ID (str): Unique identifier for the economy being analyzed. 
                          Used to filter input data and to name output files.
                          
        RAISE_ERROR (bool, optional): Flag to indicate whether to raise exceptions or warnings during execution. 
                                      If set to True, the function will halt on encountering any inconsistencies. 
                                      Defaults to False.
                                      
        
    Notes:
        - The function uses various auxiliary mappings stored in Excel sheets for data transformation.
        - DataFrames are manipulated in wide and tall formats for ease of computation.
        - Validation checks are done to ensure data integrity and schema conformity.
    """
    
    all_model_df_wides_dict = mapping_functions.find_and_load_latest_data_for_all_sources(ECONOMY_ID, sources)
    
    # Modify the data to match the plotting template
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'energy', mapping_functions.modify_losses_and_own_use_values).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2', mapping_functions.modify_losses_and_own_use_values).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_ch4', mapping_functions.modify_losses_and_own_use_values).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2e', mapping_functions.modify_losses_and_own_use_values).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_no2', mapping_functions.modify_losses_and_own_use_values).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'energy', mapping_functions.convert_electricity_output_to_twh).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'energy', mapping_functions.copy_and_modify_rows_with_conversion).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'energy', mapping_functions.modify_gas_to_gas_ccs).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'energy', mapping_functions.modify_subtotal_columns).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'energy', mapping_functions.modify_hydrogen_green_electricity).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2', mapping_functions.drop_hydrogen_transformation_rows).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2', mapping_functions.rename_sectors_and_negate_values_based_on_ccs_cap).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2', mapping_functions.copy_and_modify_power_sector_rows).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_ch4', mapping_functions.drop_hydrogen_transformation_rows).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_ch4', mapping_functions.rename_sectors_and_negate_values_based_on_ccs_cap).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_ch4', mapping_functions.copy_and_modify_power_sector_rows).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2e', mapping_functions.drop_hydrogen_transformation_rows).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2e', mapping_functions.rename_sectors_and_negate_values_based_on_ccs_cap).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_co2e', mapping_functions.copy_and_modify_power_sector_rows).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_no2', mapping_functions.drop_hydrogen_transformation_rows).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_no2', mapping_functions.rename_sectors_and_negate_values_based_on_ccs_cap).copy()
    all_model_df_wides_dict = mapping_functions.modify_dataframe_content(all_model_df_wides_dict, 'emissions_no2', mapping_functions.copy_and_modify_power_sector_rows).copy()
    # all_model_df_wides_dict['energy'][1].to_csv(f'../model_df_wide_{ECONOMY_ID}_{FILE_DATE_ID}.csv')
            
    ##############################################################################

    #import mappings:
    #these will be mappings from the names used to refer to categories shown in the plotting, to the combinations of column categories from which these categories are aggregated from.
    # Eg: Buildings is extracted by finding all values with 16_01_buildings in their sub1sectors column. Also Bunkers is extacted by finding all values with 04_international_marine_bunkers or 05_international_aviation_bunkers in their sectors column
    #The mappings are used to reduce dataframe manipulations, as a lot of code is needed to manually extract the categories from the columns when they come from so many different columns and combinations. 

    sector_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='sectors_plotting')
    # sector_plotting_mappings.columns Index(['sectors_plotting', 'sectors', 'sub1sectors', 'sub2sectors'], dtype='object')

    fuel_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='fuels_plotting')
    
    capacity_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='capacity_plotting')
    
    emissions_fuel_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='emissions_fuels_plotting')
    
    emissions_sector_plotting_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='emissions_sectors_plotting')
    # fuel_plotting_mappings.columns Index(['fuels_plotting', 'fuels', 'subfuels'], dtype='object')

    transformation_sector_mappings = pd.read_excel('../config/master_config.xlsx', sheet_name='transformation_sector_mappings')
    # transformation_sector_mappings.columns: input_fuel	transformation_sectors	sub1sectors

    charts_mapping = pd.read_excel('../config/master_config.xlsx', sheet_name='two_dimensional_plots', header = 0)
    economy_specific_chart_mapping = pd.read_excel('../config/master_config.xlsx', sheet_name='economy_specific_2d', header = 0)
    
    colors_df = pd.read_excel('../config/master_config.xlsx', sheet_name='colors')

    #take in aggregate_name_to_unit form master_config.xlsx
    aggregate_name_to_unit = pd.read_excel('../config/master_config.xlsx', sheet_name='aggregate_name_to_unit')
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
    #add any economy specific mappings to the charts_mappings
    if ECONOMY_ID in economy_specific_chart_mapping['economy'].unique():
        charts_mapping = pd.concat([charts_mapping, economy_specific_chart_mapping.loc[economy_specific_chart_mapping['economy'] == ECONOMY_ID].drop(columns=['economy'])])
        
    #witihin the emissions_fuel_plotting_mappings and emissions_sector_plotting_mappings we will create a gas column and also update the soure to ahve the gas at the end of the source name (usually source = 'emissions' but now source is one of  'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2')
    new_emissions_fuel_plotting_mappings = pd.DataFrame()
    new_emissions_sector_plotting_mappings = pd.DataFrame()
    for gas in ['CO2', 'CH4', 'CO2e', 'NO2']:
        emissions_fuel_plotting_mappings['gas'] = gas
        emissions_sector_plotting_mappings['gas'] = gas
        emissions_fuel_plotting_mappings['source'] = emissions_fuel_plotting_mappings['source'] + '_' + gas
        new_emissions_fuel_plotting_mappings = pd.concat([new_emissions_fuel_plotting_mappings, emissions_fuel_plotting_mappings])
        new_emissions_sector_plotting_mappings = pd.concat([new_emissions_sector_plotting_mappings, emissions_sector_plotting_mappings])
    emissions_fuel_plotting_mappings = new_emissions_fuel_plotting_mappings
    emissions_sector_plotting_mappings = new_emissions_sector_plotting_mappings
    
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
                                'sector_emissions_co2': {'df': emissions_sector_plotting_mappings.loc[emissions_sector_plotting_mappings['gas']=='CO2'],
                                            'columns': ['sub2sectors', 'sub1sectors', 'sectors'],
                                            'source': 'emissions_co2',
                                            'plotting_name_column': 'emissions_sectors_plotting'},
                                'fuel_emissions_co2': {'df': emissions_fuel_plotting_mappings.loc[emissions_fuel_plotting_mappings['gas']=='CO2'],
                                            'columns': ['subfuels', 'fuels'],
                                            'source': 'emissions_co2',
                                            'plotting_name_column': 'emissions_fuels_plotting'},
                                'sector_emissions_ch4': {'df': emissions_sector_plotting_mappings.loc[emissions_sector_plotting_mappings['gas']=='CH4'],
                                            'columns': ['sub2sectors', 'sub1sectors', 'sectors'],
                                            'source': 'emissions_ch4',
                                            'plotting_name_column': 'emissions_sectors_plotting'},
                                'fuel_emissions_ch4': {'df': emissions_fuel_plotting_mappings.loc[emissions_fuel_plotting_mappings['gas']=='CH4'],
                                            'columns': ['subfuels', 'fuels'],
                                            'source': 'emissions_ch4',
                                            'plotting_name_column': 'emissions_fuels_plotting'},
                                'sector_emissions_co2e': {'df': emissions_sector_plotting_mappings.loc[emissions_sector_plotting_mappings['gas']=='CO2e'],
                                            'columns': ['sub2sectors', 'sub1sectors', 'sectors'],
                                            'source': 'emissions_co2e',
                                            'plotting_name_column': 'emissions_sectors_plotting'},
                                'fuel_emissions_co2e': {'df': emissions_fuel_plotting_mappings.loc[emissions_fuel_plotting_mappings['gas']=='CO2e'],
                                            'columns': ['subfuels', 'fuels'],
                                            'source': 'emissions_co2e',
                                            'plotting_name_column': 'emissions_fuels_plotting'},
                                'sector_emissions_no2': {'df': emissions_sector_plotting_mappings.loc[emissions_sector_plotting_mappings['gas']=='NO2'],
                                            'columns': ['sub2sectors', 'sub1sectors', 'sectors'],
                                            'source': 'emissions_no2',
                                            'plotting_name_column': 'emissions_sectors_plotting'},
                                'fuel_emissions_no2': {'df': emissions_fuel_plotting_mappings.loc[emissions_fuel_plotting_mappings['gas']=='NO2'],
                                            'columns': ['subfuels', 'fuels'],
                                            'source': 'emissions_no2',
                                            'plotting_name_column': 'emissions_fuels_plotting'},
                                'capacity': {'df': capacity_plotting_mappings,
                                            'columns': ['sub4sectors','sub3sectors', 'sub2sectors', 'sub1sectors', 'sectors','sheet'],
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
        df = mapping_functions.format_plotting_mappings(df, columns,  plotting_name_column)
        all_plotting_mapping_dicts[plotting_mapping]['df'] = df
        plotting_names = plotting_names + df['plotting_name'].unique().tolist() 
        
    plotting_names = set(plotting_names)
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict = {}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['energy'] = {'sectors_plotting':'fuels_plotting', 'fuels_plotting':'sectors_plotting'}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['capacity'] = {'aggregate_name':'capacity_plotting'}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['emissions_co2'] = {'emissions_sectors_plotting':'emissions_fuels_plotting', 'emissions_fuels_plotting':'emissions_sectors_plotting'}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['emissions_ch4'] = {'emissions_sectors_plotting':'emissions_fuels_plotting', 'emissions_fuels_plotting':'emissions_sectors_plotting'}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['emissions_co2e'] = {'emissions_sectors_plotting':'emissions_fuels_plotting', 'emissions_fuels_plotting':'emissions_sectors_plotting'}
    source_and_aggregate_name_column_to_plotting_name_column_mapping_dict['emissions_no2'] = {'emissions_sectors_plotting':'emissions_fuels_plotting', 'emissions_fuels_plotting':'emissions_sectors_plotting'}
    
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
        
        economy_x = model_df_wide['economy'].unique()[0]
        model_df_wide['source'] = source
        #make model_df_wide_economy into model_df_tall
        #fgirst grab object copls as the index cols
        index_cols = model_df_wide.select_dtypes(include=['object', 'bool']).columns
        #now melt the data
        model_df_tall_all_years = pd.melt(model_df_wide, id_vars=index_cols, var_name='year', value_name='value')
        # Convert year to int
        model_df_tall_all_years['year'] = model_df_tall_all_years['year'].astype(int)

        #now, if the data contains a subtotal_layout and subtotal_results column we need to map each time period separately. this is because subtotals are different for each time period.To make it easy and siple we will just add in subtotal columns anyway and set them to False, if they dont exist.
        if 'subtotal_layout' not in model_df_tall_all_years.columns:
            model_df_tall_all_years['subtotal_layout'] = False
        if 'subtotal_results' not in model_df_tall_all_years.columns:
            model_df_tall_all_years['subtotal_results'] = False
        subtotal_to_years_map = {
            'subtotal_layout': range(EBT_EARLIEST_YEAR, OUTLOOK_BASE_YEAR+1),
            'subtotal_results': range(OUTLOOK_BASE_YEAR+1, OUTLOOK_LAST_YEAR+1)
        }
        charts_mapping_all_years = pd.DataFrame()#we will concat all the charts mappings for each year together here
        for subtotal_col in ['subtotal_layout', 'subtotal_results']:
            #make sure years in subtotal_to_years_map[subtotal_col]
            model_df_tall = model_df_tall_all_years.loc[model_df_tall_all_years['year'].isin(subtotal_to_years_map[subtotal_col])].copy()
            #filter for only subtotal_col is false
            model_df_tall = model_df_tall[model_df_tall[subtotal_col] == False].copy()
            #drop subtotal_col
            model_df_tall = model_df_tall.drop(columns=[subtotal_col])
            
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
            if source in ['energy', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2']:
                #energy and emissions_co2 are mapped to both sector and fuel columns so we needed to identify the most specific sector and fuel columns for each row and then join on them. this requires two processes below:
                new_sector_plotting_mappings = all_plotting_mapping_dicts['sector'+'_'+source]['df']
                if source in ['emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2']:
                    old_sector_plotting_mappings =emissions_sector_plotting_mappings
                    old_fuel_plotting_mappings = emissions_fuel_plotting_mappings
                elif source == 'energy':
                    old_sector_plotting_mappings= sector_plotting_mappings
                    old_fuel_plotting_mappings = fuel_plotting_mappings
                model_df_tall_sectors = mapping_functions.merge_sector_mappings(model_df_tall, new_sector_plotting_mappings,old_sector_plotting_mappings, RAISE_ERROR=RAISE_ERROR)            
                new_fuel_plotting_mappings = all_plotting_mapping_dicts['fuel'+'_'+source]['df']
                model_df_tall_sectors_fuels = mapping_functions.merge_fuel_mappings(model_df_tall_sectors, new_fuel_plotting_mappings,old_fuel_plotting_mappings, RAISE_ERROR=RAISE_ERROR)#losing access to 19_total because of filtering for lowest level values. not sure how to avoid
            elif source == 'capacity':
                #capacity is just based off sectors so its relatively simple
                new_capacity_plotting_mappings = all_plotting_mapping_dicts['capacity']['df']
                model_df_tall_capacity = mapping_functions.merge_capacity_mappings(model_df_tall, new_capacity_plotting_mappings, capacity_plotting_mappings, RAISE_ERROR=True)
                # model_df_tall = model_df_tall_capacity.copy()
                
                
            # new_emissions_co2_plotting_mappings = all_plotting_mapping_dicts['emissions_co2']['df']
            # model_df_tall_emissions_co2 = mapping_functions.merge_emissions_co2_mappings(model_df_tall, new_emissions_co2_plotting_mappings,emissions_co2_plotting_mappings, RAISE_ERROR=RAISE_ERROR)
            # breakpoint()
            
            # #call it plotting_df
            # plotting_df = model_df_tall_sectors_fuels.copy()
            #############################
            #TRANSFORMATION MAPPING
            #next step will include creating new datasets which create aggregations of data to match some of the categories plotted in the 8th edition. 
            #for example we need an aggregation of the transformation sector input and output values to create entries for Power, Refining or Hydrogen
            # breakpoint()#we get nas in the transformation sector mappings. why??
            if source in ['energy', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2']:
                input_transformation, output_transformation = mapping_functions.merge_transformation_sector_mappings(model_df_tall, transformation_sector_mappings,new_fuel_plotting_mappings,RAISE_ERROR=RAISE_ERROR)
                #concat all the dataframes together?
                plotting_df = pd.concat([model_df_tall_sectors_fuels, input_transformation, output_transformation])
                if source in ['emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2']:
                    plotting_df.rename(columns={'sectors_plotting':'emissions_sectors_plotting', 'fuels_plotting':'emissions_fuels_plotting'}, inplace=True)
            elif source == 'capacity':
                plotting_df = model_df_tall_capacity.copy()
            # elif source == 'emissions_co2':
            #     plotting_df = model_df_tall_sectors_fuels.copy()
            #     #rename sectors_plotting and fuels_plotting to emissions_sectors_plotting and emissions_fuels_plotting
            #     plotting_df.rename(columns={'sectors_plotting':'emissions_sectors_plotting', 'fuels_plotting':'emissions_fuels_plotting'}, inplace=True)
            else:
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
            economy_new_charts_mapping = mapping_functions.format_plotting_df_from_mapped_plotting_names(plotting_df, new_charts_mapping)
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
            unit_dict = {'energy': 'Petajoules', 'capacity': 'capacity', 'emissions_co2': 'MtCO2', 'emissions_ch4': 'MtCO2e', 'emissions_co2e': 'MtCO2e', 'emissions_no2': 'MtCO2e'}
            economy_new_charts_mapping['unit'] = economy_new_charts_mapping['source'].map(unit_dict)
            #check there are no dupes in aggregate name in unit df
            if aggregate_name_to_unit.duplicated(['aggregate_name', 'source']).any():
                raise Exception('There are duplicates in the aggregate_name column in aggregate_name_to_unit')
            #based on aggregate_name in economy_new_charts_mapping, set unit to the unit in aggregate_name_to_unit
            economy_new_charts_mapping = economy_new_charts_mapping.merge(aggregate_name_to_unit, on=['aggregate_name', 'source'], how='left', suffixes=('','_y'))
            #if unit_y is not null, set unit to unit_y
            economy_new_charts_mapping.loc[economy_new_charts_mapping['unit_y'].notnull(), 'unit'] = economy_new_charts_mapping['unit_y']
            #drop unit_y
            economy_new_charts_mapping = economy_new_charts_mapping.drop(columns=['unit_y', 'economy'])
            
            #rename scenarios to scenario
            economy_new_charts_mapping.rename(columns={'scenarios':'scenario'}, inplace=True)
            #set the year column to int
            economy_new_charts_mapping.year = economy_new_charts_mapping.year.astype(int)
            
            economy_new_charts_mapping['dimensions'] = '2D'
            #check the columns are the ones we expect:
            missing_cols = [x for x in EXPECTED_COLS if x not in economy_new_charts_mapping.columns]
            extra_cols = [x for x in economy_new_charts_mapping.columns if x not in EXPECTED_COLS]
            if len(extra_cols) > 0 or len(missing_cols) > 0:
                raise Exception(f'There are missing or extra columns in charts_mapping. Extra cols: {extra_cols}. Missing cols: {missing_cols}')
            
            economy_new_charts_mapping = mapping_functions.format_chart_titles(economy_new_charts_mapping, ECONOMY_ID)
            #############################
            
            #concat to charts_mapping_all_years 
            charts_mapping_all_years = pd.concat([charts_mapping_all_years, economy_new_charts_mapping])
        
        # Modify dataframe to include percentage_bar chart_type
        charts_mapping_all_years = mapping_functions.add_percentage_bar_chart_type(charts_mapping_all_years)
        
        # Save the processed data to a pickle file
        charts_mapping_all_years.to_pickle(f'../intermediate_data/data/charts_mapping_{source}_{economy_x}_{FILE_DATE_ID}.pkl')
        print(f"Data for {economy_x} {source} saved.")
        # charts_mapping_all_years.to_csv(f'../intermediate_data/charts_mapping_{source}_{economy_x}_{FILE_DATE_ID}.csv')
        
        # If sources is emissions_co2, return the filtered data
        
        if source == 'emissions_co2':
            total_emissions_co2 = charts_mapping_all_years[(charts_mapping_all_years['sheet_name'] == 'Emissions_co2') & (charts_mapping_all_years['plotting_name'].isin(['Agriculture','Buildings', 'Industry', 'Non-specified', 'Own-use and losses', 'Power_input', 'Transport'])) & (charts_mapping_all_years['aggregate_name'] == 'TFEC')].copy()
            # Group by scenario and year, and sum the values
            total_emissions_co2 = total_emissions_co2.groupby(['scenario', 'year'])['value'].sum().reset_index()
        if source == 'emissions_ch4':
            total_emissions_ch4 = charts_mapping_all_years[(charts_mapping_all_years['sheet_name'] == 'Emissions_ch4') & (charts_mapping_all_years['plotting_name'].isin(['Agriculture','Buildings', 'Industry', 'Non-specified', 'Own-use and losses', 'Power_input', 'Transport'])) & (charts_mapping_all_years['aggregate_name'] == 'TFEC')].copy()
            total_emissions_ch4 = total_emissions_ch4.groupby(['scenario', 'year'])['value'].sum().reset_index()
        if source == 'emissions_co2e':
            total_emissions_co2e = charts_mapping_all_years[(charts_mapping_all_years['sheet_name'] == 'Emissions_co2e') & (charts_mapping_all_years['plotting_name'].isin(['Agriculture','Buildings', 'Industry', 'Non-specified', 'Own-use and losses', 'Power_input', 'Transport'])) & (charts_mapping_all_years['aggregate_name'] == 'TFEC')].copy()
            total_emissions_co2e = total_emissions_co2e.groupby(['scenario', 'year'])['value'].sum().reset_index()
        if source == 'emissions_no2':
            total_emissions_no2 = charts_mapping_all_years[(charts_mapping_all_years['sheet_name'] == 'Emissions_no2') & (charts_mapping_all_years['plotting_name'].isin(['Agriculture','Buildings', 'Industry', 'Non-specified', 'Own-use and losses', 'Power_input', 'Transport'])) & (charts_mapping_all_years['aggregate_name'] == 'TFEC')].copy()
            total_emissions_no2 = total_emissions_no2.groupby(['scenario', 'year'])['value'].sum().reset_index()
            
    return total_emissions_co2, total_emissions_ch4, total_emissions_co2e, total_emissions_no2

#%%
# FILE_DATE_ID = '20231110'
# ECONOMY_ID = '19_THA'
# map_9th_data_to_plotting_template_handler(FILE_DATE_ID, ECONOMY_ID, RAISE_ERROR=False)
#%%


# #take in C:\Users\finbar.maunsell\github\9th_edition_visualisation\input_data\19_THA\merged_file_capacity_19_THA_20231110.csv, drop fuels columns and keep only where sectors == 09_total_transformation_sector or 15_transport_sector
# x = pd.read_csv(r'C:\Users\finbar.maunsell\github\9th_edition_visualisation\input_data\19_THA\merged_file_capacity_19_THA_20231110.csv')
# x = x[(x['sectors'] == '09_total_transformation_sector') | (x['sectors'] == '15_transport_sector')]
# x = x.drop(columns=['fuels', 'subfuels']).drop_duplicates()
# x.to_csv(r'C:\Users\finbar.maunsell\github\9th_edition_visualisation\input_data\19_THA\merged_file_capacity_19_THA_20231110.csv')