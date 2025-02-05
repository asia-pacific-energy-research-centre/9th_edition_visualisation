
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
import mapping_functions
#%%

def map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS):#, total_emissions_co2, total_emissions_ch4, total_emissions_co2e, total_emissions_no2):
    #some data cant fit into the balance format, so we import it here. it will be plotted in the best way to communicate that data, so not necessarily in the balances format.

    #to keep things tidy we will follow the process of: 
    #for each unique dataset we want to plot, create a function where we extract and calculate the data, and then put it in the format we want the tabel to be in, and then put it in a dictionary with the kind of plot we would like to use as an entry.
    #e.g. 
    all_1d_plotting_dfs = pd.DataFrame()
    population_df, gdp_df, gdp_per_capita_df = extract_macro_data(ECONOMY_ID)
    all_1d_plotting_dfs = pd.concat([all_1d_plotting_dfs, population_df, gdp_df, gdp_per_capita_df], axis=0)
    energy_intensity, emissions_co2_intensity, raw_energy_intensity_df, raw_emissions_co2_intensity_df, emissions_co2_melt = calculate_and_extract_intensity_data(ECONOMY_ID)
    
    all_1d_plotting_dfs = pd.concat([all_1d_plotting_dfs, energy_intensity, emissions_co2_intensity], axis=0)
    
    renewable_share_df, electricity_renewable_share = calculate_and_extract_renewable_share_data(ECONOMY_ID)
    all_1d_plotting_dfs = pd.concat([all_1d_plotting_dfs, renewable_share_df, electricity_renewable_share], axis=0)
    kaya_identity_df_COMBINED = calculate_and_extract_kaya_identity_data_COMBINED(ECONOMY_ID, raw_energy_intensity_df, emissions_co2_melt, raw_emissions_co2_intensity_df)
    kaya_identity_df = calculate_and_extract_kaya_identity_data(ECONOMY_ID, raw_energy_intensity_df, emissions_co2_melt, raw_emissions_co2_intensity_df)
    breakpoint()
    all_1d_plotting_dfs = pd.concat([all_1d_plotting_dfs, kaya_identity_df, kaya_identity_df_COMBINED], axis=0)
    
    charts_mapping_1d = map_all_1d_plotting_dfs_to_charts_mapping(all_1d_plotting_dfs, EXPECTED_COLS)
    
    charts_mapping_1d = mapping_functions.format_chart_titles(charts_mapping_1d, ECONOMY_ID)
    # charts_mapping_1d.to_csv('../intermediate_data/charts_mapping_1d.csv')
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
    
    # If plotting_name is emissions_components, set them to the same value as temp_plotting_name
    charts_mapping.loc[charts_mapping['plotting_name'] == 'emissions_components', 'plotting_name'] = charts_mapping.loc[charts_mapping['plotting_name'] == 'emissions_components', 'temp_plotting_name']
    charts_mapping.loc[charts_mapping['plotting_name'] == 'emissions_components_combined', 'plotting_name'] = charts_mapping.loc[charts_mapping['plotting_name'] == 'emissions_components_combined', 'temp_plotting_name']
    charts_mapping.drop(columns=['temp_plotting_name'], inplace=True)
    
    # charts_mapping.to_csv('../intermediate_data/charts_mapping_1d.csv')
    #check for any rows that are left only
    if (charts_mapping._merge == 'left_only').any():
        breakpoint()
        charts_mapping.to_csv('../intermediate_data/charts_mapping_1d.csv')
        raise Exception('There are rows in charts_mapping that are left only. This should not happen.')
    #drop merge col
    charts_mapping.drop(columns=['_merge'], inplace=True)
    #create table_id
    charts_mapping['table_id'] = charts_mapping.apply(lambda x: f"{x['source']}_{x['sheet_name']}_{x['table_number']}", axis=1)
    #check the columns are the ones we expect:
    missing_cols = [x for x in EXPECTED_COLS if x not in charts_mapping.columns]
    extra_cols = [x for x in charts_mapping.columns if x not in EXPECTED_COLS]
    if len(extra_cols) > 0 or len(missing_cols) > 0:
        breakpoint()
        raise Exception(f'There are missing or extra columns in charts_mapping. Extra cols: {extra_cols}. Missing cols: {missing_cols}')
    
    return charts_mapping


def calculate_aggregate_data(macro_data, AGGREGATE_ECONOMY_MAPPING, ECONOMY_ID):
    #first filter for the economies we want to aggregate
    
    macro_data_AGG = macro_data[macro_data.economy_code.isin(AGGREGATE_ECONOMY_MAPPING[ECONOMY_ID])].copy()
    
    #add new economy code
    macro_data_AGG['economy_code'] = ECONOMY_ID
    macro_data_AGG['economy'] = ECONOMY_ID
    
    if len(macro_data) == 0:
        breakpoint()
        raise Exception(f'There is no data for the economies in the aggregate {ECONOMY_ID} in the macro data file. Please check the macro data file.')
    #sum the values for each year
    # 'economy_code', 'economy', 'year', 'variable', 'value', 'units'
    #extract gdp_per_cpita since thats a bit different (we want to clac it as gdp/population rather than an avg of the gdp_per_capita)
    macro_data_AGG = macro_data_AGG[macro_data_AGG.variable.isin(['population', 'real_GDP'])].copy()
    macro_data_AGG = macro_data_AGG.groupby(['economy_code', 'economy', 'year', 'variable', 'units']).sum().reset_index().copy()
    #now we want to calculate gdp_per_capita as gdp/population *1000
    population_AGG = macro_data_AGG[macro_data_AGG.variable == 'population'].copy()
    population_AGG.rename(columns={'value':'population'}, inplace=True)
    gdp_AGG = macro_data_AGG[macro_data_AGG.variable == 'real_GDP'].copy()
    gdp_AGG = pd.merge(gdp_AGG, population_AGG[['economy_code', 'year', 'population']], how='left', on=['economy_code', 'year'])
    gdp_AGG['value'] = gdp_AGG['value']/gdp_AGG['population'] * 1000
    gdp_AGG['variable'] = 'GDP_per_capita'
    gdp_AGG.drop(columns=['population'], inplace=True)
    #concatenate with the rest of the data
    macro_data_AGG = pd.concat([macro_data_AGG, gdp_AGG], axis=0)
    macro_data = macro_data_AGG.copy()
    
    return macro_data
    
    
def extract_macro_data(ECONOMY_ID):
    #load in macro data
    #if there are multiple macro data files throw an error
    #find latest data in macro:
    macro_data_file = find_most_recent_file_date_id(directory_path=f'../input_data/macro/', filename_part = 'APEC_GDP_data_',RETURN_DATE_ID = False)
    macro_data = pd.read_csv(f'../input_data/macro/{macro_data_file}')
    # macro_data = pd.read_csv(f'../input_data/macro/APEC_GDP_data_2024_09_02.csv')
    #if economy is one o f the aggregate ones the we want to create a aggregate of all the necessary economies, if its not already in the data!
    
    if ECONOMY_ID in AGGREGATE_ECONOMY_MAPPING.keys() and ECONOMY_ID not in macro_data.economy_code.unique():
        macro_data = calculate_aggregate_data(macro_data, AGGREGATE_ECONOMY_MAPPING, ECONOMY_ID)
            
    macro_data = macro_data[macro_data.economy_code == ECONOMY_ID].copy()
    if len(macro_data) == 0:
        breakpoint()
        raise Exception(f'There is no data for the economy {ECONOMY_ID} in the macro data file.')
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
    #to do this we need to use total energy consumption and total emissions_co2 and then divide by gdp. note that this will not go into detail on sectors, if that is ever needed it will need to be part of the 2d plots as it will 'intensity by sector'
    
    #######
    #get data ready
    all_model_df_wides_dict = mapping_functions.find_and_load_latest_data_for_all_sources(ECONOMY_ID, ['energy', 'emissions_co2'])
    energy_w_subtotals = all_model_df_wides_dict['energy'][1]
    emissions_co2_w_subtotals = all_model_df_wides_dict['emissions_co2'][1]

    years_cols = [x for x in energy_w_subtotals.columns if re.match(r'\d\d\d\d', x)]
    
    #make all values after the base year 0 in historical data
    historical_data = emissions_co2_w_subtotals.copy()
    historical_data.drop(columns=PROJ_YEARS_str, inplace=True)
    proj_data = emissions_co2_w_subtotals.copy()
    proj_data.drop(columns=HIST_YEARS_str, inplace=True)
    
    #filter for only not subtotal_layout in historical data and not subtotal_results in proj data
    historical_data = historical_data[(historical_data.subtotal_layout==False)]
    proj_data = proj_data[(proj_data.subtotal_results==False)].copy()
    #merge them and sum
    emissions_co2 = pd.concat([historical_data, proj_data], axis=0)
    emissions_co2.fillna(0, inplace=True)
    
    historical_data = energy_w_subtotals.copy()
    historical_data.drop(columns=PROJ_YEARS_str, inplace=True)
    proj_data = energy_w_subtotals.copy()
    proj_data.drop(columns=HIST_YEARS_str, inplace=True)
    #filter for only not subtotal_layout in historical data and not subtotal_results in proj data
    historical_data = historical_data[(historical_data.subtotal_layout==False)]
    proj_data = proj_data[(proj_data.subtotal_results==False)].copy()
    #merge them and sum
    energy = pd.concat([historical_data, proj_data], axis=0)
    
    #set any nas in the energy data to 0
    energy.fillna(0, inplace=True)
    #######
    
    #rename scenarios to scenario
    energy.rename(columns={'scenarios': 'scenario'}, inplace=True)
    emissions_co2.rename(columns={'scenarios': 'scenario'}, inplace=True)
    #load in 
    # for some reason, electricity is double counted in historic energy_total values. We will use 07_total_primary_energy_supply instead because Kaya identity is based on primary energy supply.
    # energy_total = energy[(energy.sectors == '13_total_final_energy_consumption') & (energy.fuels == '19_total') & (~energy.subtotal_layout) & (~energy.subtotal_results)].copy()
    energy_total = energy[(energy.sectors == '07_total_primary_energy_supply') & (energy.fuels == '19_total')]
    #sum
    energy_total = energy_total[HIST_YEARS_str + PROJ_YEARS_str + ['scenario']].copy()
    # Group the filtered data by the 'scenario' column
    energy_total = energy_total.groupby('scenario').sum().reset_index()
    ###########################################################################
    
    #do a quick check that we arent getting more than one row per scenario since we are setting subtotals to true for any total final consumption rows.
    unique_energy_scenarios = energy_total.scenario.unique()
    if len(energy_total) > len(unique_energy_scenarios):
        breakpoint()
        raise Exception('There are more rows in energy_total than there are unique scenarios. This should not happen.')
    
    ###########################################################################
    #NOTE FOR THIS WE CAN USE THE ['sectors'] = '20_total_combustion_emissions' CATEGORY!
    
    emissions_co2_total_combustion = emissions_co2[(emissions_co2.sectors == '20_total_combustion_emissions') & (~emissions_co2.fuels.isin(['19_total','20_total_renewables','21_modern_renewables']))].copy()
    #sum
    emissions_co2_total_combustion =emissions_co2_total_combustion[years_cols + ['scenario']].copy()
    # Group the filtered data by the 'scenario' column
    emissions_co2_total_combustion = emissions_co2_total_combustion.groupby('scenario').sum().reset_index()
    ###########################################################################
        
    #double check we ahve as many rows as energy df
    if len(emissions_co2_total_combustion) != len(energy_total):
        breakpoint()
        raise Exception('The number of rows in emissions_co2_total_combustion is not equal to the number of rows in energy_total. This should not happen.')
    
    ###########################################################################
    
    #quickly check for duplicates
    if energy_total.duplicated().any():
        breakpoint()
        raise Exception('There are duplicates in energy_total')
    if emissions_co2_total_combustion.duplicated().any():
        breakpoint()
        raise Exception('There are duplicates in emissions_co2_total_combustion')
    
    #now melt
    energy_total_melt = energy_total.melt(id_vars=['scenario'], var_name='year', value_name='energy_total')
    emissions_co2_total_combustion_melt = emissions_co2_total_combustion.melt(id_vars=['scenario'], var_name='year', value_name='value')

    #make year int
    energy_total_melt['year'] = energy_total_melt['year'].astype(int)
    emissions_co2_total_combustion_melt['year'] = emissions_co2_total_combustion_melt['year'].astype(int)

    # Filter data for years within the specified range
    energy_total_melt = energy_total_melt[(energy_total_melt['year'] >= MIN_YEAR) & (energy_total_melt['year'] <= OUTLOOK_LAST_YEAR)]
    emissions_co2_total_combustion_melt = emissions_co2_total_combustion_melt[(emissions_co2_total_combustion_melt['year'] >= MIN_YEAR) & (emissions_co2_total_combustion_melt['year'] <= OUTLOOK_LAST_YEAR)]

    #join with macro data wiht only gdp in it
    population, real_gdp, gdppc = extract_macro_data(ECONOMY_ID)
    real_gdp.drop(columns=['plotting_name'], inplace=True)
    
    energy_intensity = pd.merge(energy_total_melt, real_gdp, how='left', on=['year'])
    # Energy intensity is calculated as TPES divided by GDP
    energy_intensity['value'] = energy_intensity['energy_total']/energy_intensity['value']
    energy_intensity.drop(columns=['energy_total'], inplace=True)

    emissions_co2_total_combustion_intensity = pd.merge(emissions_co2_total_combustion_melt, energy_total_melt, how='left', on=['year', 'scenario'])
    # emissions_co2 intensity is calculated as gross emissions_co2 divided by TPES (CO2 intensity of TPES)
    emissions_co2_total_combustion_intensity['value'] = emissions_co2_total_combustion_intensity['value']/emissions_co2_total_combustion_intensity['energy_total']
    emissions_co2_total_combustion_intensity.drop(columns=['energy_total'], inplace=True)
    
    # Copy and save data for kaya identity calculation
    raw_energy_intensity_df = energy_intensity.copy()
    raw_emissions_co2_intensity_df = emissions_co2_total_combustion_intensity.copy()
    emissions_co2_melt = emissions_co2_total_combustion_melt.copy()
    
    # Normalizing the data to index it to 100 for the year 2005
    base_year = 2005
    
    # Function to normalize the dataframe
    def normalize_to_base_year(df, base_year):
        # Find the base year value for each scenario
        base_values = df[df['year'] == base_year].set_index('scenario')['value']
        # Merge base year values back to the main dataframe to divide
        df = df.join(base_values, on='scenario', rsuffix='_base')
        # Normalize and scale to 100
        df['value'] = (df['value'] / df['value_base']) * 100
        # Drop the base value column after calculation
        df.drop(columns=['value_base'], inplace=True)
        return df
    
    # Normalize energy and emissions_co2 intensity
    energy_intensity = normalize_to_base_year(energy_intensity, base_year)
    emissions_co2_intensity = normalize_to_base_year(emissions_co2_total_combustion_intensity, base_year)
    
    # # Set values to NaN for 'target' scenarios between MIN_YEAR and OUTLOOK_BASE_YEAR
    # energy_intensity.loc[(energy_intensity['scenario'] == 'target') & (energy_intensity['year'] >= MIN_YEAR) & (energy_intensity['year'] < OUTLOOK_BASE_YEAR), 'value'] = np.nan
    # emissions_co2_intensity.loc[(emissions_co2_intensity['scenario'] == 'target') & (emissions_co2_intensity['year'] >= MIN_YEAR) & (emissions_co2_intensity['year'] < OUTLOOK_BASE_YEAR), 'value'] = np.nan
    
    #now we have energy_intensity and emissions_co2_intensity, we need to put them in the format we want to plot them in
    energy_intensity['source'] = 'intensity'
    energy_intensity['plotting_name'] = 'energy_intensity'
    emissions_co2_intensity['source'] = 'intensity'
    emissions_co2_intensity['plotting_name'] = 'emissions_co2_intensity'

    #change unit
    energy_intensity['unit'] = 'PJ/million_gdp_2017_usd_ppp'
    emissions_co2_intensity['unit'] = 'tons CO2/petajoule'
    
    # #cnacatenate and return
    # energy_and_emissions_co2_intensity = pd.concat([energy_intensity, emissions_co2_intensity], axis=0)
    return energy_intensity, emissions_co2_intensity, raw_energy_intensity_df, raw_emissions_co2_intensity_df, emissions_co2_melt


def calculate_and_extract_renewable_share_data(ECONOMY_ID):
    #TODO CALCAULTE THIS ONCE WE GET AN UNDERSTANDUNG OF HOW TO CALCULATE IT. FOR NOW JSUT USE TOTAL RENEWABLES / TOTAL ENERGY
    #load in energy data
    all_model_df_wides_dict = mapping_functions.find_and_load_latest_data_for_all_sources(ECONOMY_ID, ['energy'])
    energy_w_subtotals = all_model_df_wides_dict['energy'][1]
    
    energy_hist = energy_w_subtotals.copy()
    energy_proj = energy_w_subtotals.copy()
    energy_hist.drop(columns=PROJ_YEARS_str, inplace=True)
    energy_proj.drop(columns=HIST_YEARS_str, inplace=True)
    energy_hist= energy_hist[(energy_hist.subtotal_layout==False)]
    energy_proj = energy_proj[(energy_proj.subtotal_results==False)].copy()
    energy = pd.concat([energy_hist, energy_proj], axis=0)
    #set any nas in the energy data to 0
    energy.fillna(0, inplace=True)
    #sum all to get rid of stray 0s
    other_cols = [x for x in energy.columns if x not in PROJ_YEARS_str + HIST_YEARS_str]
    energy = energy.groupby(other_cols).sum().reset_index()
    
    #extract toal final consumption and total renewables
    energy_total = energy[(energy.sectors == '13_total_final_energy_consumption') & (energy.fuels == '19_total')].copy()
    
    energy_renewables = energy[(energy.sectors == '13_total_final_energy_consumption') & (energy.fuels == '21_modern_renewables')].copy()
    
    # Extract total electricity generated from renewable sources and total electricity generation
    electricity_renewables = energy[(energy.sectors == '18_electricity_output_in_gwh') & (energy.sub1sectors == 'x') & (energy.fuels == '20_total_renewables')].copy()
    electricity_total = energy[(energy.sectors == '18_electricity_output_in_gwh') & (energy.sub1sectors == 'x') & (energy.fuels == '19_total')].copy()
    
    #melt them
    years_cols = [x for x in energy_total.columns if re.match(r'\d\d\d\d', x)]
    energy_total =energy_total[years_cols + ['scenarios']].copy()
    energy_renewables =energy_renewables[years_cols + ['scenarios']].copy()
    energy_total_melt = energy_total.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='energy_total')
    energy_renewables_melt = energy_renewables.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='energy_renewables')
    
    # Melt electricity data
    years_cols = [x for x in electricity_total.columns if re.match(r'\d\d\d\d', x)]
    electricity_total = electricity_total[years_cols + ['scenarios']].copy()
    electricity_renewables = electricity_renewables[years_cols + ['scenarios']].copy()
    electricity_total_melt = electricity_total.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='electricity_total')
    electricity_renewables_melt = electricity_renewables.melt(id_vars=['scenarios'], value_vars=years_cols, var_name='year', value_name='electricity_renewables')
    
    #make year int
    energy_total_melt['year'] = energy_total_melt['year'].astype(int)
    energy_renewables_melt['year'] = energy_renewables_melt['year'].astype(int)
    #merge them
    renewable_share = pd.merge(energy_total_melt, energy_renewables_melt, how='left', on=['scenarios', 'year'])
    #calculate share
    renewable_share['value'] = (renewable_share['energy_renewables']/renewable_share['energy_total']) * 100
    
    # Change year to integer
    electricity_total_melt['year'] = electricity_total_melt['year'].astype(int)
    electricity_renewables_melt['year'] = electricity_renewables_melt['year'].astype(int)
    # Merge electricity data
    electricity_renewable_share = pd.merge(electricity_total_melt, electricity_renewables_melt, how='left', on=['scenarios', 'year'])
    # Calculate the share of renewables in electricity generation
    electricity_renewable_share['value'] = (electricity_renewable_share['electricity_renewables'] / electricity_renewable_share['electricity_total']) * 100
    
    # # Set values to NaN for 'target' scenarios between MIN_YEAR and OUTLOOK_BASE_YEAR
    # renewable_share.loc[(renewable_share['scenarios'] == 'target') & (renewable_share['year'] >= MIN_YEAR) & (renewable_share['year'] < OUTLOOK_BASE_YEAR), 'value'] = np.nan
    # electricity_renewable_share.loc[(electricity_renewable_share['scenarios'] == 'target') & (electricity_renewable_share['year'] >= MIN_YEAR) & (electricity_renewable_share['year'] < OUTLOOK_BASE_YEAR), 'value'] = np.nan
    
    # we need to put them in the format we want to plot them in
    renewable_share['source'] = 'renewables_share'
    renewable_share['plotting_name'] = 'renewables_share'
    renewable_share['unit'] = 'Modern renewables % of total final energy consumption'
    renewable_share.drop(columns=['energy_total', 'energy_renewables'], inplace=True)
    renewable_share.rename(columns={'scenarios':'scenario'}, inplace=True)
    
    # Format electricity data
    electricity_renewable_share['source'] = 'renewables_share'
    electricity_renewable_share['plotting_name'] = 'renewables_share_in_electricity_generation'
    electricity_renewable_share['unit'] = 'Renewables % of total electricity generation'
    electricity_renewable_share.drop(columns=['electricity_total', 'electricity_renewables'], inplace=True)
    electricity_renewable_share.rename(columns={'scenarios':'scenario'}, inplace=True)
    
    return renewable_share, electricity_renewable_share

def calculate_and_extract_kaya_identity_data_COMBINED(ECONOMY_ID, raw_energy_intensity_df, emissions_co2_melt, raw_emissions_co2_intensity_df):   
    def get_factor(df, base_year, last_year):
        base_value = df.loc[df['year'] == base_year, 'value'].values[0]
        last_value = df.loc[df['year'] == last_year, 'value'].values[0]
        return last_value / base_value
    
    def add_new_rows(kaya_df, year, factor, scenario, previous_value):
        new_value = factor * previous_value
        new_value_diff = new_value - previous_value
        plotting_name = 'rise' if new_value_diff > 0 else 'fall'
        new_value_diff = abs(new_value_diff)
        kaya_df = pd.concat([kaya_df, pd.DataFrame({
            'scenario': [scenario],
            'year': [year],
            'plotting_name': [plotting_name],
            'value': [new_value_diff]
        })], ignore_index=True)
        
        base_value = previous_value if plotting_name == 'rise' else previous_value - new_value_diff
        new_row = pd.DataFrame({
            'scenario': [scenario],
            'year': [year],
            'plotting_name': ['base'],
            'value': [base_value]
        })
        kaya_df = pd.concat([kaya_df, new_row], ignore_index=True)
        
        return kaya_df, new_value

    # Load the required data
    population, real_gdp, gdppc = extract_macro_data(ECONOMY_ID)
    
    # Filter total emissions_co2 data for the required years
    total_emissions_co2 = emissions_co2_melt[emissions_co2_melt['year'].isin([OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR])].copy()
    # Select specific columns to copy
    kaya_identity_df = total_emissions_co2[['scenario', 'year', 'value']].copy()
    kaya_identity_df['plotting_name'] = 'initial'
    
    # where scenario is reference, Change OUTLOOK_BASE_YEAR to 3000 and OUTLOOK_LAST_YEAR to 3004, and where scenario is target, drop the year =  OUTLOOK_BASE_YEAR and then set OUTLOOK_LAST_YEAR to 3006
    kaya_identity_df.loc[(kaya_identity_df['year'] == OUTLOOK_BASE_YEAR) & (kaya_identity_df['scenario'] == 'reference'), 'year'] = 3000
    kaya_identity_df.loc[(kaya_identity_df['year'] == OUTLOOK_LAST_YEAR) & (kaya_identity_df['scenario'] == 'reference'), 'year'] = 3004
    kaya_identity_df = kaya_identity_df[~((kaya_identity_df['year'] == OUTLOOK_BASE_YEAR) & (kaya_identity_df['scenario'] == 'target'))]
    kaya_identity_df.loc[(kaya_identity_df['year'] == OUTLOOK_LAST_YEAR) & (kaya_identity_df['scenario'] == 'target'), 'year'] = 3006
    
    # Calculate factors
    population_factor = get_factor(population, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    gdppc_factor = get_factor(gdppc, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    
    # for scenario in ['reference', 'target']:
    # Initial value for year 3000
    year_3000_value = kaya_identity_df[(kaya_identity_df['year'] == 3000) & (kaya_identity_df['scenario'] == 'reference')]['value'].values[0]
    
    # Add population factor rows
    kaya_identity_df, population_adjusted_value = add_new_rows(kaya_identity_df, 3001, population_factor, 'reference', year_3000_value)
    
    # Add GDP per capita factor rows
    kaya_identity_df, gdppc_adjusted_value = add_new_rows(kaya_identity_df, 3002, gdppc_factor, 'reference', population_adjusted_value)
    
    #WE'LL DO THIS FOR REFERENCE FIRST AND THEN DO IT FOR TARGET
    
    #REFERENCE############################################################################################################
    # Add energy intensity factor rows togerhter and add them to emissions_co2 intensity factor rows
    energy_intensity_factor_REF = get_factor(raw_energy_intensity_df[raw_energy_intensity_df['scenario'] == 'reference'], OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    emissions_co2_intensity_factor_REF = get_factor(raw_emissions_co2_intensity_df[raw_emissions_co2_intensity_df['scenario'] == 'reference'], OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    
    kaya_identity_df_temp, temp_base_energy_intensity = add_new_rows(kaya_identity_df, 3003, energy_intensity_factor_REF, 'reference', gdppc_adjusted_value)
    
    kaya_identity_df_temp, temp_base_emissions_intensity = add_new_rows(kaya_identity_df_temp, 3004, emissions_co2_intensity_factor_REF, 'reference', temp_base_energy_intensity)#gdppc_adjusted_value)
    
    #for base for final year for ref, use the 3004 initial value row (which is the final emissions for ref scenario)
    base_3003 = kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'] == 'initial') & (kaya_identity_df_temp['year'] == 3004) & (kaya_identity_df_temp['scenario'] == 'reference')]
    base_3003.loc[:, 'year'] = 3003
    base_3003.loc[:, 'plotting_name'] = 'base'
    kaya_identity_df = pd.concat([kaya_identity_df, base_3003], ignore_index=True)
    
    #Then for the fall or rise for the intensity bar for ref, we add together where plotting name is either fall or rise and year is 3004 and 3003 to get the intensity for ref. we will identify if its colored for a fall or rise based on whether it has to drop or increase to reach the base value for 3003
    fall_rise_ref_energy = kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'].isin(['fall', 'rise'])) & (kaya_identity_df_temp['year'] == 3003) & (kaya_identity_df_temp['scenario'] == 'reference')]['value'].values[0]
    fall_rise_ref_emissions = kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'].isin(['fall', 'rise'])) & (kaya_identity_df_temp['year'] == 3004) & (kaya_identity_df_temp['scenario'] == 'reference')]['value'].values[0]

    # Adjust the sign based on whether it's a rise or fall
    if kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'] == 'rise') & (kaya_identity_df_temp['year'] == 3003) & (kaya_identity_df_temp['scenario'] == 'reference')].any().any():
        fall_rise_ref_energy = -fall_rise_ref_energy
    if kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'] == 'rise') & (kaya_identity_df_temp['year'] == 3004) & (kaya_identity_df_temp['scenario'] == 'reference')].any().any():
        fall_rise_ref_emissions = -fall_rise_ref_emissions

    fall_rise_ref = fall_rise_ref_energy + fall_rise_ref_emissions
    #It is a fall if the initial for 3004 is equal to basefor 3003. If not then its a rise.
    initial_3004 = kaya_identity_df[(kaya_identity_df['plotting_name'] == 'initial') & (kaya_identity_df['year'] == 3004)]['value'].values[0]
    base_3003 = kaya_identity_df[(kaya_identity_df['plotting_name'] == 'base') & (kaya_identity_df['year'] == 3003)]['value'].values[0]
    
    if initial_3004 == base_3003:
        fall_or_rise_ref = 'fall'
    else:
        fall_or_rise_ref = 'rise'
    #idenitfy if its a fall or rise
    kaya_identity_df = pd.concat([kaya_identity_df, pd.DataFrame({
        'scenario': ['reference'],
        'year': [3003],
        'plotting_name': [fall_or_rise_ref],
        'value': [fall_rise_ref]
    })], ignore_index=True)
        
    #TARGET############################################################################################################
    # Add energy intensity factor rows togerhter and add them to emissions_co2 intensity factor rows
    energy_intensity_factor_TGT = get_factor(raw_energy_intensity_df[raw_energy_intensity_df['scenario'] == 'target'], OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    emissions_co2_intensity_factor_TGT = get_factor(raw_emissions_co2_intensity_df[raw_emissions_co2_intensity_df['scenario'] == 'target'], OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    # and now do similar for tgt - the fall will be done the same as ref except we takeaway the tgt initial from the ref initial:
    kaya_identity_df_temp, energy_adjusted_value = add_new_rows(kaya_identity_df, 3005, energy_intensity_factor_TGT, 'target', gdppc_adjusted_value)
    kaya_identity_df_temp, energy_adjusted_value = add_new_rows(kaya_identity_df_temp, 3006, emissions_co2_intensity_factor_TGT, 'target', gdppc_adjusted_value)
    
    initial_tgt = kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'] == 'initial') & (kaya_identity_df_temp['year'] == 3006) & (kaya_identity_df_temp['scenario'] == 'target')]['value'].values[0]
    initial_ref = kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'] == 'initial') & (kaya_identity_df_temp['year'] == 3004) & (kaya_identity_df_temp['scenario'] == 'reference')]['value'].values[0]
    fall_tgt = initial_ref - initial_tgt #we can pretty safely assume this is a fall since the ref is the base and ref is always higher than tgt in terms of emissions 
    kaya_identity_df = pd.concat([kaya_identity_df, pd.DataFrame({
        'scenario': ['target'],
        'year': [3005],
        'plotting_name': ['fall'],
        'value': [fall_tgt]
    })], ignore_index=True)
    
    #and for base for final year for tgt, use the 3006 value row
    base_3005 = kaya_identity_df_temp[(kaya_identity_df_temp['plotting_name'] == 'initial') & (kaya_identity_df_temp['year'] == 3006) & (kaya_identity_df_temp['scenario'] == 'target')]
    base_3005.loc[:, 'year'] = 3005
    base_3005.loc[:, 'plotting_name'] = 'base'
    kaya_identity_df = pd.concat([kaya_identity_df, base_3005], ignore_index=True)
    
    #now duplicate the df but call scenario reference and target respectively
    kaya_identity_df_ref = kaya_identity_df.copy()
    kaya_identity_df_tgt = kaya_identity_df.copy()
    kaya_identity_df_ref['scenario'] = 'reference'
    kaya_identity_df_tgt['scenario'] = 'target'
    kaya_identity_df = pd.concat([kaya_identity_df_ref, kaya_identity_df_tgt], axis=0)
    # Finalize the DataFrame
    
    kaya_identity_df.rename(columns={'plotting_name': 'temp_plotting_name'}, inplace=True)
    #add '_combined' to the temp_plotting_name
    kaya_identity_df['temp_plotting_name'] = kaya_identity_df['temp_plotting_name'] + '_combined'
    kaya_identity_df['plotting_name'] = 'emissions_components_combined'
    kaya_identity_df['unit'] = 'million tonnes'
    kaya_identity_df['source'] = 'kaya'
    kaya_identity_df['plotting_name_column'] = 'variable'
    return kaya_identity_df


def calculate_and_extract_kaya_identity_data(ECONOMY_ID, raw_energy_intensity_df, emissions_co2_melt, raw_emissions_co2_intensity_df):
    
    def get_factor(df, base_year, last_year):
        base_value = df.loc[df['year'] == base_year, 'value'].values[0]
        last_value = df.loc[df['year'] == last_year, 'value'].values[0]
        return last_value / base_value
    
    def add_new_rows(kaya_df, year, factor, scenario, previous_value):
        new_value = factor * previous_value
        new_value_diff = new_value - previous_value
        plotting_name = 'rise' if new_value_diff > 0 else 'fall'
        new_value_diff = abs(new_value_diff)
        kaya_df = pd.concat([kaya_df, pd.DataFrame({
            'scenario': [scenario],
            'year': [year],
            'plotting_name': [plotting_name],
            'value': [new_value_diff]
        })], ignore_index=True)
        
        base_value = previous_value if plotting_name == 'rise' else previous_value - new_value_diff
        new_row = pd.DataFrame({
            'scenario': [scenario],
            'year': [year],
            'plotting_name': ['base'],
            'value': [base_value]
        })
        kaya_df = pd.concat([kaya_df, new_row], ignore_index=True)
        
        return kaya_df, new_value

    # Load the required data
    population, real_gdp, gdppc = extract_macro_data(ECONOMY_ID)
    
    # Filter total emissions_co2 data for the required years
    total_emissions_co2 = emissions_co2_melt[emissions_co2_melt['year'].isin([OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR])].copy()
    # Select specific columns to copy
    kaya_identity_df = total_emissions_co2[['scenario', 'year', 'value']].copy()
    kaya_identity_df['plotting_name'] = 'initial'
    
    # Change OUTLOOK_BASE_YEAR to 3000 and OUTLOOK_LAST_YEAR to 3005
    kaya_identity_df.loc[kaya_identity_df['year'] == OUTLOOK_BASE_YEAR, 'year'] = 3000
    kaya_identity_df.loc[kaya_identity_df['year'] == OUTLOOK_LAST_YEAR, 'year'] = 3005
    
    # Calculate factors
    population_factor = get_factor(population, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    gdppc_factor = get_factor(gdppc, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    
    for scenario in ['reference', 'target']:
        # Initial value for year 3000
        year_3000_value = kaya_identity_df[(kaya_identity_df['year'] == 3000) & (kaya_identity_df['scenario'] == scenario)]['value'].values[0]
        
        # Add population factor rows
        kaya_identity_df, population_adjusted_value = add_new_rows(kaya_identity_df, 3001, population_factor, scenario, year_3000_value)
        
        # Add GDP per capita factor rows
        kaya_identity_df, gdppc_adjusted_value = add_new_rows(kaya_identity_df, 3002, gdppc_factor, scenario, population_adjusted_value)
        
        # Add energy intensity factor rows
        energy_intensity_factor = get_factor(raw_energy_intensity_df[raw_energy_intensity_df['scenario'] == scenario], OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
        kaya_identity_df, energy_adjusted_value = add_new_rows(kaya_identity_df, 3003, energy_intensity_factor, scenario, gdppc_adjusted_value)
        
        # Add emissions_co2 intensity factor rows
        emissions_co2_intensity_factor = get_factor(raw_emissions_co2_intensity_df[raw_emissions_co2_intensity_df['scenario'] == scenario], OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
        kaya_identity_df, _ = add_new_rows(kaya_identity_df, 3004, emissions_co2_intensity_factor, scenario, energy_adjusted_value)
    
    # Finalize the DataFrame
    kaya_identity_df.rename(columns={'plotting_name': 'temp_plotting_name'}, inplace=True)
    kaya_identity_df['plotting_name'] = 'emissions_components'
    kaya_identity_df['unit'] = 'million tonnes'
    kaya_identity_df['source'] = 'kaya'
    kaya_identity_df['plotting_name_column'] = 'variable'
    return kaya_identity_df