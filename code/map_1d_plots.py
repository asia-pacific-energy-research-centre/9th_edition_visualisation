
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
#%%

def map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS):
    #some data cant fit into the balance format, so we import it here. it will be plotted in the best way to communicate that data, so not necessarily in the balances format.

    #to keep things tidy we will follow the process of: 
    #for each unique dataset we want to plot, create a function where we extract and calculate the data, and then put it in the format we want the tabel to be in, and then put it in a dictionary with the kind of plot we would like to use as an entry.
    #e.g. 
    breakpoint()
    all_1d_plotting_dfs = pd.DataFrame()
    population_df, gdp_df, gdp_per_capita_df = extract_macro_data(ECONOMY_ID)
    all_1d_plotting_dfs = pd.concat([all_1d_plotting_dfs, population_df, gdp_df, gdp_per_capita_df], axis=0)
    
    energy_intensity_df, emissions_intensity_df = calculate_and_extract_intensity_data(ECONOMY_ID)
    all_1d_plotting_dfs = pd.concat([all_1d_plotting_dfs, energy_intensity_df, emissions_intensity_df], axis=0)
    
    renewable_share_df = calculate_and_extract_renewable_share_data(ECONOMY_ID)
    all_1d_plotting_dfs = pd.concat([all_1d_plotting_dfs, renewable_share_df], axis=0)
    
    
    #when it comes to very specific charts, we can use a specific chart name which when referenced will call a specific function to create the chart. e.g. 'decomposition_chart' will call the function create_decomposition_chart() which will create the chart.
    #TODO: add decomposition chart
    # decomposition_df = calculate_and_extract_decomposition_data()
    #plotting_dict['Decomposition'] = ((decomposition_df, 'decomposition_waterfall', 'Decomposition', 'Decomposition', None),)
    charts_mapping_1d = map_all_1d_plotting_dfs_to_charts_mapping(all_1d_plotting_dfs, EXPECTED_COLS)
    
    charts_mapping_1d = mapping_functions.format_chart_tiles(charts_mapping_1d, ECONOMY_ID)
    breakpoint()
    return charts_mapping_1d
    

def map_all_1d_plotting_dfs_to_charts_mapping(all_1d_plotting_dfs, EXPECTED_COLS):
    # charts_mapping.head(2)
    # source economy  table_number   sheet_name chart_type plotting_name_column  \
    # 0  energy  19_THA             1  Agriculture       line       fuels_plotting   
    # 1  energy  19_THA             1  Agriculture       line       fuels_plotting   

    # plotting_name aggregate_name_column aggregate_name   scenario  year  \
    # 0       Biomass      sectors_plotting    Agriculture  reference  1980   
    # 1       Biomass      sectors_plotting    Agriculture  reference  1981   

    #             table_id  value        unit   dimensions chart_title
    # 0  energy_Agriculture_1    0.0  Petajoules  2D
    # 1  energy_Agriculture_1    0.0  Petajoules  2D
    
    #need to:
    #insert nans for aggregate_name_column, aggregate_name, scenario.
    #need to create table_id,table_number, dimensions. these should be come up with using master_config>one_dimensional_plots
    charts_mapping_template = pd.read_excel('../config/master_config.xlsx', sheet_name='one_dimensional_plots')
    #cols: source	sheet_name	table_number	chart_type	plotting_name	chart_title
    all_1d_plotting_dfs['aggregate_name_column'] = np.nan
    all_1d_plotting_dfs['aggregate_name'] = np.nan
    
    all_1d_plotting_dfs['dimensions'] = '1D'

    # all_1d_plotting_dfs.to_csv('../intermediate_data/all_1d_plotting_dfs.csv')
    
    #join onto charts_mapping_template using a left join so we get one to many:
    charts_mapping = pd.merge(charts_mapping_template, all_1d_plotting_dfs, how='left', on=['source', 'plotting_name'], indicator=True)
    # charts_mapping.to_csv('../intermediate_data/charts_mapping_1d.csv')
    #check for any rows that are left only
    if (charts_mapping._merge == 'left_only').any():
        breakpoint()
        charts_mapping.to_csv('../intermediate_data/charts_mapping_1d.csv')
        raise Exception('There are rows in charts_mapping that are left only. This should not happen.')
    #drop merge col
    charts_mapping.drop(columns=['_merge'], inplace=True)
    
    charts_mapping['table_id'] = charts_mapping.apply(lambda x: f"{x['source']}_{x['sheet_name']}_{x['table_number']}", axis=1)
    
    #check the columns are the ones we expect:
    missing_cols = [x for x in EXPECTED_COLS if x not in charts_mapping.columns]
    extra_cols = [x for x in charts_mapping.columns if x not in EXPECTED_COLS]
    if len(extra_cols) > 0 or len(missing_cols) > 0:
        breakpoint()
        raise Exception(f'There are missing or extra columns in charts_mapping. Extra cols: {extra_cols}. Missing cols: {missing_cols}')
    
    return charts_mapping

def extract_macro_data(ECONOMY_ID):
    #load in macro data
    #if there are multiple macro data files throw an error
    macro_data_files = glob.glob(f'../input_data/macro/APEC_GDP_data_*.csv')
    if len(macro_data_files) > 1:
        breakpoint()
        raise Exception(f'There are multiple macro data files in ../macro. There should only be one. Please remove the extra files and try again.')

    macro_data = pd.read_csv(macro_data_files[0])
    macro_data = macro_data[macro_data.economy_code == ECONOMY_ID].copy()
    #drop economy var
    macro_data.drop(columns=['economy', 'economy_code'], inplace=True)
    #rename variable to plotting_name
    macro_data.rename(columns={'variable':'plotting_name', 'scenarios':'scenario', 'units':'unit'}, inplace=True)
    #create columns called source and plotting_name_column
    macro_data['source'] = 'macro'
    macro_data['plotting_name_column'] = 'variable'
    
    # Filter for years between MIN_YEAR and OUTLOOK_LAST_YEAR
    macro_data = macro_data[(macro_data['year'] >= MIN_YEAR) & (macro_data['year'] <= OUTLOOK_LAST_YEAR)]

    # #filter for plotting_name in population, real_GDP, GDP_per_capita
    # #POPULATION
    population = macro_data[macro_data['plotting_name'] == 'population'].copy()

    # #GDP
    real_gdp = macro_data[macro_data['plotting_name'] == 'real_GDP'].copy()

    # #GDP per capita
    gdppc = macro_data[macro_data['plotting_name'] == 'GDP_per_capita'].copy()

    return population, real_gdp, gdppc

def calculate_and_extract_intensity_data(ECONOMY_ID):
    #to do this we need to use total energy consumption and total emissions and then divide by gdp. note that this will not go into detail on sectors, if that is ever needed it will need to be part of the 2d plots as it will 'intensity by sector'
    breakpoint()
    all_model_df_wides_dict = mapping_functions.find_and_load_latest_data_for_all_sources(ECONOMY_ID, ['energy', 'emissions'])
    energy = all_model_df_wides_dict['energy'][1]
    emissions = all_model_df_wides_dict['emissions'][1]

    #load in 
    # for some reason, electricity is double counted in historic energy_total values. We will use 07_total_primary_energy_supply instead because Kaya identity is based on primary energy supply.
    # energy_total = energy[(energy.sectors == '13_total_final_energy_consumption') & (energy.fuels == '19_total') & (~energy.subtotal_layout) & (~energy.subtotal_results)].copy()
    energy_total = energy[(energy.sectors == '07_total_primary_energy_supply') & (energy.fuels == '19_total') & (~energy.subtotal_layout) & (~energy.subtotal_results)].copy()
    #do a quick check that we arent getting more than one row per scenario since we are setting subtotals to true for any total final consumption rows.
    unique_energy_scenarios = energy_total.scenarios.unique()
    if len(energy_total) > len(unique_energy_scenarios):
        breakpoint()
        raise Exception('There are more rows in energy_total than there are unique scenarios. This should not happen.')

    emissions_total = emissions[(emissions.sectors == '07_total_primary_energy_supply') & (emissions.subfuels == 'x')].copy()
    # Group the filtered data by the 'scenarios' column
    emissions_total = emissions_total.groupby('scenarios').sum().reset_index().copy()
    unique_emissions_scenarios = emissions_total.scenarios.unique()
    if len(emissions_total) > len(unique_emissions_scenarios):
        breakpoint()
        raise Exception('There are more rows in emissions_total than there are unique scenarios. This should not happen.')

    # emissions_total.to_csv('../intermediate_data/emissions_total.csv')

    #now melt and join with macro data on year.
    #first identify the years cols so we can keep only them and scenario
    years_cols = [x for x in energy_total.columns if re.match(r'\d\d\d\d', x)]
    energy_total =energy_total[years_cols + ['scenarios']].copy()
    years_cols = [x for x in emissions_total.columns if re.match(r'\d\d\d\d', x)]
    emissions_total =emissions_total[years_cols + ['scenarios']].copy()

    #quickly check for duplicates
    if energy_total.duplicated().any():
        breakpoint()
        raise Exception('There are duplicates in energy_total')
    if emissions_total.duplicated().any():
        breakpoint()
        raise Exception('There are duplicates in emissions_total')

    #now melt
    energy_total_melt = energy_total.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='energy_total')
    emissions_total_melt = emissions_total.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='emissions_total')

    #make year int
    energy_total_melt['year'] = energy_total_melt['year'].astype(int)
    emissions_total_melt['year'] = emissions_total_melt['year'].astype(int)

    # Filter data for years within the specified range
    energy_total_melt = energy_total_melt[(energy_total_melt['year'] >= MIN_YEAR) & (energy_total_melt['year'] <= OUTLOOK_LAST_YEAR)]
    emissions_total_melt = emissions_total_melt[(emissions_total_melt['year'] >= MIN_YEAR) & (emissions_total_melt['year'] <= OUTLOOK_LAST_YEAR)]

    #join with macro data wiht only gdp in it
    population, real_gdp, gdppc = extract_macro_data(ECONOMY_ID)
    real_gdp.drop(columns=['plotting_name'], inplace=True)
    real_gdp['value'] = real_gdp['value']/100 #to get 10,000 which seems to be similar magnitude to energy and emissions
    breakpoint()
    energy_intensity = pd.merge(energy_total_melt, real_gdp, how='left', on=['year'])
    energy_intensity['value'] = energy_intensity['energy_total']/energy_intensity['value']
    energy_intensity.drop(columns=['energy_total'], inplace=True)

    emissions_intensity = pd.merge(emissions_total_melt, real_gdp, how='left', on=['year'])
    emissions_intensity['value'] = emissions_intensity['emissions_total']/emissions_intensity['value']
    emissions_intensity.drop(columns=[ 'emissions_total'], inplace=True)
    
    # Normalizing the data to index it to 100 for the year 2005
    base_year = 2005
    
    # Function to normalize the dataframe
    def normalize_to_base_year(df, base_year):
        # Find the base year value for each scenario
        base_values = df[df['year'] == base_year].set_index('scenarios')['value']
        # Merge base year values back to the main dataframe to divide
        df = df.join(base_values, on='scenarios', rsuffix='_base')
        # Normalize and scale to 100
        df['value'] = (df['value'] / df['value_base']) * 100
        # Drop the base value column after calculation
        df.drop(columns=['value_base'], inplace=True)
        return df
    
    # Normalize energy and emissions intensity
    energy_intensity = normalize_to_base_year(energy_intensity, base_year)
    emissions_intensity = normalize_to_base_year(emissions_intensity, base_year)
    
    # Set values to NaN for 'target' scenarios between MIN_YEAR and OUTLOOK_BASE_YEAR
    energy_intensity.loc[(energy_intensity['scenarios'] == 'target') & (energy_intensity['year'] >= MIN_YEAR) & (energy_intensity['year'] < OUTLOOK_BASE_YEAR), 'value'] = np.nan
    emissions_intensity.loc[(emissions_intensity['scenarios'] == 'target') & (emissions_intensity['year'] >= MIN_YEAR) & (emissions_intensity['year'] < OUTLOOK_BASE_YEAR), 'value'] = np.nan
    
    #now we have energy_intensity and emissions_intensity, we need to put them in the format we want to plot them in
    energy_intensity['source'] = 'intensity'
    energy_intensity['plotting_name'] = 'energy_intensity'
    emissions_intensity['source'] = 'intensity'
    emissions_intensity['plotting_name'] = 'emissions_intensity'

    #change unit to PJ/million_gdp_2017_usd_ppp or MtCO2/million_gdp_2017_usd_ppp
    energy_intensity['unit'] = 'PJ/ten_thousand_gdp_2017_usd_ppp'
    emissions_intensity['unit'] = 'MtCO2/ten_thousand_gdp_2017_usd_ppp'

    #rena,e , 'scenarios':'scenario'
    energy_intensity.rename(columns={'scenarios':'scenario'}, inplace=True)
    emissions_intensity.rename(columns={'scenarios':'scenario'}, inplace=True)
    # #cnacatenate and return
    # energy_and_emissions_intensity = pd.concat([energy_intensity, emissions_intensity], axis=0)
    return energy_intensity, emissions_intensity

# def calculate_and_extract_intensity_data(ECONOMY_ID):
#     #to do this we need to use total energy consumption and total emissions and then divide by gdp. note that this will not go into detail on sectors, if that is ever needed it will need to be part of the 2d plots as it will 'intensity by sector'
#     breakpoint()
#     all_model_df_wides_dict = mapping_functions.find_and_load_latest_data_for_all_sources(ECONOMY_ID, ['energy', 'emissions'])
#     energy = all_model_df_wides_dict['energy'][1]
#     emissions = all_model_df_wides_dict['emissions'][1]

#     #load in 
#     energy_total = energy[(energy.sectors == '12_total_final_consumption') & (energy.fuels == '19_total') & (~energy.subtotal_layout) & (~energy.subtotal_results)].copy()
#     #do a quick check that we arent getting more than one row per scenario since we are setting subtotals to true for any total final consumption rows.
#     unique_energy_scenarios = energy_total.scenarios.unique()
#     if len(energy_total) > len(unique_energy_scenarios):
#         breakpoint()
#         raise Exception('There are more rows in energy_total than there are unique scenarios. This should not happen.')

#     emissions_total = emissions[(emissions.sectors == '12_total_final_consumption') & (emissions.fuels == '19_total') & (~emissions.subtotal_layout) & (~emissions.subtotal_results)].copy()
#     unique_emissions_scenarios = emissions_total.scenarios.unique()
#     if len(emissions_total) > len(unique_emissions_scenarios):
#         breakpoint()
#         raise Exception('There are more rows in emissions_total than there are unique scenarios. This should not happen.')

#     # emissions_total.to_csv('../intermediate_data/emissions_total.csv')

#     #now melt and join with macro data on year.
#     #first identify the years cols so we can keep only them and scenario
#     years_cols = [x for x in energy_total.columns if re.match(r'\d\d\d\d', x)]
#     energy_total =energy_total[years_cols + ['scenarios']].copy()
#     years_cols = [x for x in emissions_total.columns if re.match(r'\d\d\d\d', x)]
#     emissions_total =emissions_total[years_cols + ['scenarios']].copy()

#     #quickly check for duplicates
#     if energy_total.duplicated().any():
#         breakpoint()
#         raise Exception('There are duplicates in energy_total')
#     if emissions_total.duplicated().any():
#         breakpoint()
#         raise Exception('There are duplicates in emissions_total')

#     #now melt
#     energy_total_melt = energy_total.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='energy_total')
#     emissions_total_melt = emissions_total.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='emissions_total')

#     #make year int
#     energy_total_melt['year'] = energy_total_melt['year'].astype(int)
#     emissions_total_melt['year'] = emissions_total_melt['year'].astype(int)

#     #join with macro data wiht only gdp in it
#     population, real_gdp, gdppc = extract_macro_data(ECONOMY_ID)
#     real_gdp.drop(columns=['plotting_name'], inplace=True)
#     real_gdp['value'] = real_gdp['value']/100 #to get 10,000 which seems to be similar magnitude to energy and emissions
#     breakpoint()
#     energy_intensity = pd.merge(energy_total_melt, real_gdp, how='left', on=['year'])
#     energy_intensity['value'] = energy_intensity['energy_total']/energy_intensity['value']
#     energy_intensity.drop(columns=['energy_total'], inplace=True)

#     emissions_intensity = pd.merge(emissions_total_melt, real_gdp, how='left', on=['year'])
#     emissions_intensity['value'] = emissions_intensity['emissions_total']/emissions_intensity['value']
#     emissions_intensity.drop(columns=[ 'emissions_total'], inplace=True)
        
#     #now we have energy_intensity and emissions_intensity, we need to put them in the format we want to plot them in
#     energy_intensity['source'] = 'intensity'
#     energy_intensity['plotting_name'] = 'energy_intensity'
#     emissions_intensity['source'] = 'intensity'
#     emissions_intensity['plotting_name'] = 'emissions_intensity'

#     #change unit to PJ/million_gdp_2017_usd_ppp or MtCO2/million_gdp_2017_usd_ppp
#     energy_intensity['unit'] = 'PJ/ten_thousand_gdp_2017_usd_ppp'
#     emissions_intensity['unit'] = 'MtCO2/ten_thousand_gdp_2017_usd_ppp'

#     #rena,e , 'scenarios':'scenario'
#     energy_intensity.rename(columns={'scenarios':'scenario'}, inplace=True)
#     emissions_intensity.rename(columns={'scenarios':'scenario'}, inplace=True)
#     # #cnacatenate and return
#     # energy_and_emissions_intensity = pd.concat([energy_intensity, emissions_intensity], axis=0)
#     return energy_intensity, emissions_intensity


def calculate_and_extract_renewable_share_data(ECONOMY_ID):
    #TODO CALCAULTE THIS ONCE WE GET AN UNDERSTANDUNG OF HOW TO CALCULATE IT. FOR NOW JSUT USE TOTAL RENEWABLES / TOTAL ENERGY
    
    #load in energy data
    all_model_df_wides_dict = mapping_functions.find_and_load_latest_data_for_all_sources(ECONOMY_ID, ['energy'])
    energy = all_model_df_wides_dict['energy'][1]
    #extract toal final consumption and total renewables
    energy_total = energy[(energy.sectors == '12_total_final_consumption') & (energy.fuels == '19_total') & (~energy.subtotal_layout) & (~energy.subtotal_results)].copy()
    energy_total.to_csv('../intermediate_data/energy_total.csv')
    energy_renewables = energy[(energy.sectors == '12_total_final_consumption') & (energy.fuels == '21_modern_renewables') & (~energy.subtotal_layout) & (~energy.subtotal_results)].copy()
    energy_renewables.to_csv('../intermediate_data/energy_renewables.csv')
    
    #melt them
    years_cols = [x for x in energy_total.columns if re.match(r'\d\d\d\d', x)]
    energy_total =energy_total[years_cols + ['scenarios']].copy()
    energy_renewables =energy_renewables[years_cols + ['scenarios']].copy()
    energy_total_melt = energy_total.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='energy_total')
    energy_renewables_melt = energy_renewables.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='energy_renewables')
    #make year int
    energy_total_melt['year'] = energy_total_melt['year'].astype(int)
    energy_renewables_melt['year'] = energy_renewables_melt['year'].astype(int)
    #merge them
    renewable_share = pd.merge(energy_total_melt, energy_renewables_melt, how='left', on=['scenarios', 'year'])
    #calculate share
    renewable_share['value'] = (renewable_share['energy_renewables']/renewable_share['energy_total']) * 100
    
    # Set values to NaN for 'target' scenarios between MIN_YEAR and OUTLOOK_BASE_YEAR
    renewable_share.loc[(renewable_share['scenarios'] == 'target') & (renewable_share['year'] >= MIN_YEAR) & (renewable_share['year'] < OUTLOOK_BASE_YEAR), 'value'] = np.nan
    
    renewable_share.to_csv('../intermediate_data/renewables_share.csv')
    
    # we need to put them in the format we want to plot them in
    renewable_share['source'] = 'renewable_share'
    renewable_share['plotting_name'] = 'renewable_share'
    renewable_share['unit'] = 'Modern renewables % of total final consumption'
    renewable_share.drop(columns=['energy_total', 'energy_renewables'], inplace=True)
    renewable_share.rename(columns={'scenarios':'scenario'}, inplace=True)
    
    return renewable_share
