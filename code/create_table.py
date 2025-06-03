

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

def extract_macro_value(macro_df: pd.DataFrame, variable: str, base_year: int, last_year: int):
    """
    Extract the macro value for a given variable for both base and target years.
    
    If the variable is 'population' and the units are in thousands,
    converts the value to millions.
    """
    base_row = macro_df[(macro_df['variable'] == variable) & (macro_df['year'] == base_year)]
    last_row = macro_df[(macro_df['variable'] == variable) & (macro_df['year'] == last_year)]
    
    if not base_row.empty:
        base_val = base_row.iloc[0]['value']
        base_unit = base_row.iloc[0]['units']
    else:
        base_val = np.nan
        base_unit = ""
    
    if not last_row.empty:
        last_val = last_row.iloc[0]['value']
        last_unit = last_row.iloc[0]['units']
    else:
        last_val = np.nan
        last_unit = ""
    
    # Convert population from thousands to millions, if needed.
    if variable == 'population' and base_unit.lower() == "thousands":
        base_val = base_val / 1000
        last_val = last_val / 1000
    return int(round(base_val)), int(round(last_val))

def calculate_pct_change(ref_value, target_value):
    """
    Calculate the percent change between ref_value and target_value.
    Returns np.nan if the reference value is zero or invalid.
    """
    try:
        if ref_value and ref_value != 0:
            return ((target_value - ref_value) / ref_value) * 100
        else:
            return np.nan
    except TypeError:
        return np.nan

def extract_dataset_value(df, economy, scenario, filters, base_year, last_year):
    """
    Filter a wide-format dataset (e.g. energy) by economy, scenario, plus any additional filters.
    
    If a filter value is a list, an isin() clause is used.
    Returns a tuple (base_val, last_val) computed as the sum of the values in each year column.
    """
    subset = df.loc[
        (df["economy"] == economy) &
        (df["scenarios"] == scenario)
    ]
    
    for col_name, col_value in filters.items():
        # Skip keys that are not used for filtering.
        if col_name in ['dataset', 'variable', 'adjustment']:
            continue
        if isinstance(col_value, list):
            subset = subset[subset[col_name].isin(col_value)]
        else:
            subset = subset[subset[col_name] == col_value]
    
    if subset.empty:
        return (np.nan, np.nan)
    
    base_val = subset[str(base_year)].sum()
    last_val = subset[str(last_year)].sum()
    return (base_val, last_val)

def calculate_other_data(datasets, ECONOMY_ID, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR):
    """
    Calculate additional values from the provided datasets that don't come directly from
    the macro, energy, emissions, or capacity datasets.
    
    (This function is left as a placeholder for future additions.)
    """
    pass

def create_table(datasets, 
                        ECONOMY_ID="01_AUS", 
                        OUTLOOK_BASE_YEAR=2022, 
                        OUTLOOK_LAST_YEAR=2060, 
                        macro_df=pd.DataFrame()):
    """
    Create a table summarizing energy and macro data for a given economy
    
    The table compares OUTLOOK_BASE_YEAR to OUTLOOK_LAST_YEAR and calculates the percentage change.
    
    Parameters:
      df_energy       : A wide-format DataFrame with year columns (e.g., 2022, 2060).
      ECONOMY_ID      : The economy code, e.g. "01_AUS".
      OUTLOOK_BASE_YEAR: The base year (e.g., 2022).
      OUTLOOK_LAST_YEAR: The target year (e.g., 2060).
      macro_df        : The macro dataset DataFrame (to provide macro values).
      
    Returns:
      A DataFrame with multi-level columns showing the base and target year values and % change.
    """
    # Define lists for fuel/subfuel categories if needed.
    BIOENERGY_SUBFUELS = [
        "16_01_biogas",  "16_05_biogasoline", "16_06_biodiesel",
        "16_07_bio_jet_kerosene", "16_08_other_liquid_biofuels", "15_01_fuelwood_and_woodwaste", "15_02_bagasse",
        "15_03_charcoal", "15_04_black_liquor", "15_05_other_biomass",
        "15_solid_biomass_unallocated"
    ]#"16_02_industrial_waste", since we are strict for charts, we should be strict about our def of bioenergy here too "16_03_municipal_solid_waste_renewable",
    # "16_04_municipal_solid_waste_nonrenewable","16_09_other_sources",
    # "16_others_unallocated", 
    OTHER_SUBFUELS = ["16_02_industrial_waste", "16_03_municipal_solid_waste_renewable",
                      "16_04_municipal_solid_waste_nonrenewable", "16_09_other_sources", "16_others_unallocated"
    ]
    HYDROGEN_SUBFUELS = ["16_x_ammonia", "16_x_efuel", "16_x_hydrogen"]
    LOW_CARBON_ELECTRICITY_FUELS = [
        "09_nuclear", "10_hydro", "11_geothermal", "12_solar",
        "13_tide_wave_ocean", "14_wind", "17_x_green_electricity"
    ]
    RENEWABLE_ELECTRICITY_FUELS = LOW_CARBON_ELECTRICITY_FUELS  # For this example
    
    # Build the row_filters dictionary.
    # Section headers are marked by a value of None.
    row_filters = {
        "Macroeconomic": None,
        "Population (million)": {'variable': 'population'},
        "GDP (billion, USD PPP 2017)": {'variable': 'real_GDP', 'adjustment': 1/1e3},
        
        "Energy Demand": None,  # Section header.
        "Buildings (PJ)" :  {"sub1sectors": "16_01_buildings", 'dataset': 'energy'},
        "Industry (PJ)" : {"sectors": "14_industry_sector", 'dataset': 'energy'},
        "Transport (PJ)" : {"sectors": "15_transport_sector", 'dataset': 'energy'},
        "Non-energy (PJ)": {"sectors": "17_nonenergy_use", 'dataset': 'energy'},

        "Electricity & hydrogen": None,    # Section header.
        "Generation (TWh)": {"sectors": "18_electricity_output_in_gwh", 'dataset': 'energy', 'adjustment': 1/1e3},
        'Renewable Share (%)': {"sectors": "19_renewable_share", 'dataset': 'other'},  # Skipped for now.
        'Capacity (GW)': {"sheet": "generation_capacity", 'dataset': 'capacity'},#, 'adjustment': 1/1e3},           # Skipped for now.
        'Capacity Factor (%)': {"sectors": "21_capacity_factor", 'dataset': 'other'},       # Skipped for now.
        
        'Hydrogen-based fuels supply (PJ)': {"sectors": ["07_total_primary_energy_supply", '09_total_transformation_sector_POSITIVE'], "subfuels": HYDROGEN_SUBFUELS, 'dataset': 'energy'},
        
        "Total Primary Energy Supply": None,  # Section header.
        "Coal & coal products (PJ)":   {"sectors": "07_total_primary_energy_supply", 
                        "fuels": ["01_coal", "02_coal_products", "03_peat", "04_peat_products"],
                        'dataset': 'energy'},
        "Petroleum products & crude (PJ)":    {"sectors": "07_total_primary_energy_supply", 
                        "fuels": ["06_crude_oil_and_ngl", "07_petroleum_products", "05_oil_shale_and_oil_sands"],
                        'dataset': 'energy'},
        "Natural gas (PJ)":    {"sectors": "07_total_primary_energy_supply", "fuels": ["08_gas"],
                        'dataset': 'energy'},
        'Bioenergy & waste (PJ)': {"sectors": "07_total_primary_energy_supply", "subfuels": BIOENERGY_SUBFUELS + OTHER_SUBFUELS,
                           'dataset': 'energy'},
        'Renewables for electricity generation (PJ)': {"sectors": "07_total_primary_energy_supply", 
                                                       "fuels": RENEWABLE_ELECTRICITY_FUELS,
                                                       'dataset': 'energy'},
        'Nuclear (PJ)': {"sectors": "07_total_primary_energy_supply", "fuels": ["09_nuclear"],
                         'dataset': 'energy'},
        'Emissions': None,  # Section header.
        'CO2 net Emissions (million Tonnes)': {"sectors": "21_total_combustion_emissions_net", 
                                               "fuels": "23_total_combustion_emissions_net",
                                               'dataset': 'emissions_co2'},
        'CO2e net Emissions (million Tonnes)': {"sectors": "21_total_combustion_emissions_net", 
                                                "fuels": "23_total_combustion_emissions_net",
                                                'dataset': 'emissions_co2e'},
    }
    
    #within the energy data, createrows for 09_total_transformation_sector_POSITIVE. they will be where the 09_total_transformation_sector is used but also wehre the values are postivie. 
    transformation_output = datasets['energy'][datasets['energy']['sectors'] == '09_total_transformation_sector']
    years = [col for col in transformation_output.columns if re.match(r'^\d{4}$', col)]
    # Filter out rows where any of the values are negative.
    transformation_output = transformation_output[~(transformation_output[years] < 0).any(axis=1)].copy()
    transformation_output['sectors'] = '09_total_transformation_sector_POSITIVE'
    # Append the filtered rows to the energy dataset.
    datasets['energy'] = pd.concat([datasets['energy'], transformation_output], ignore_index=True)
    
    # Create multi-level columns for the table.
    cols = pd.MultiIndex.from_tuples([
        ("Reference", f"{OUTLOOK_BASE_YEAR}"),
        ("Reference", f"{OUTLOOK_LAST_YEAR}"),
        ("Reference", "% Change"),
        ("Target",    f"{OUTLOOK_BASE_YEAR}"),
        ("Target",    f"{OUTLOOK_LAST_YEAR}"),
        ("Target",    "% Change")
    ])
    
    # Process each row defined in the row_filters dictionary.
    row_names = list(row_filters.keys())
    table_data = []
    for row_name in row_names:
        # if row_name in ['Hydrogen-based fuels (PJ)']:#, 'CO2 net Emissions (million Tonnes)', 'CO2e net Emissions (million Tonnes)']:
        #     breakpoint()
        
        filters = row_filters[row_name]
        # if row_name =='Capacity (GW)':
        #     breakpoint()  # check why our numbers are so wrong
        # For section headers (or blank rows), add an empty row.
        if not filters:
            table_data.append([""] * len(cols))
            continue
        
        # Determine from which dataset to extract data.
        dataset_name = filters.get('dataset') if 'dataset' in filters else 'macro'
        
        # Skip rows that reference the "other" dataset.
        if dataset_name == 'other':
            table_data.append([""] * len(cols))
            continue
        
        # If using macro data, extract via the variable key.
        if dataset_name == 'macro':
            variable = filters.get('variable')
            if variable is None:
                
                base_val_ref, last_val_ref = (np.nan, np.nan)
                base_val_tgt, last_val_tgt = (np.nan, np.nan)
            else:
                base_val_ref, last_val_ref = extract_macro_value(macro_df, variable, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
                base_val_tgt, last_val_tgt = extract_macro_value(macro_df, variable, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
            
        else:
            # For datasets such as energy, capacity, or emissions,
            # call extract_dataset_value.
            base_val_ref, last_val_ref = extract_dataset_value(
                df=datasets[dataset_name],
                economy=ECONOMY_ID,
                scenario='reference',
                filters=filters,
                base_year=OUTLOOK_BASE_YEAR,
                last_year=OUTLOOK_LAST_YEAR
            )
            base_val_tgt, last_val_tgt = extract_dataset_value(
                df=datasets[dataset_name],
                economy=ECONOMY_ID,
                scenario='target',
                filters=filters,
                base_year=OUTLOOK_BASE_YEAR,
                last_year=OUTLOOK_LAST_YEAR
            ) 
    
        # Calculate percent change.
        pct_change_ref = calculate_pct_change(base_val_ref, last_val_ref)
        pct_change_tgt = calculate_pct_change(base_val_tgt, last_val_tgt)
        pct_str_ref = f"{int(round(pct_change_ref))}%" if not np.isnan(pct_change_ref) else " "
        pct_str_tgt = f"{int(round(pct_change_tgt))}%" if not np.isnan(pct_change_tgt) else " "

        adjustment = filters.get('adjustment', 1)
        # Mirror the same values for Reference and Target (adjust if you have separate scenarios).
        
        # if row_name in ['Hydrogen-based fuels (PJ)']:
        #     breakpoint()
        #double check none are nans. if so then raise an error
        
        # if np.isnan(base_val_ref) or np.isnan(last_val_ref) or np.isnan(base_val_tgt) or np.isnan(last_val_tgt):
        #     breakpoint()
        #     print(f"NaN values found for row: {row_name}")
        # row_vals = [
        #     int(round(base_val_ref*adjustment)) if not np.isnan(base_val_ref) else 0,  # Reference, base-year
        #     int(round(last_val_ref*adjustment)) if not np.isnan(last_val_ref) else 0,  # Reference, target-year
        #     pct_str_ref if not np.isnan(pct_change_ref) else " ",  # Reference, % Change
        #     int(round(base_val_tgt*adjustment)) if not np.isnan(base_val_tgt) else 0,  # Target, base-year
        #     int(round(last_val_tgt*adjustment)) if not np.isnan(last_val_tgt) else 0,  # Target, target-year
        #     pct_str_tgt if not np.isnan(pct_change_tgt) else " "  # Target, % Change
        # ]    
        def round_sig(x, sig=2):
            if np.isnan(x):
                return 0
            if x == 0:
                return 0
            return int(round(x, -int(np.floor(np.log10(abs(x))) - (sig - 1))))

        row_vals = [
            round_sig(base_val_ref * adjustment) if not np.isnan(base_val_ref) else 0,  # Reference, base-year
            round_sig(last_val_ref * adjustment) if not np.isnan(last_val_ref) else 0,  # Reference, target-year
            pct_str_ref if not np.isnan(pct_change_ref) else " ",  # Reference, % Change
            round_sig(base_val_tgt * adjustment) if not np.isnan(base_val_tgt) else 0,  # Target, base-year
            round_sig(last_val_tgt * adjustment) if not np.isnan(last_val_tgt) else 0,  # Target, target-year
            pct_str_tgt if not np.isnan(pct_change_tgt) else " "  # Target, % Change
        ]    
        table_data.append(row_vals)
    
    # Create the final DataFrame.
    df_table = pd.DataFrame(table_data, index=row_names, columns=cols)
    print(df_table.to_string())
    # Optionally, copy to clipboard for Excel/Word:
    # df_table.to_clipboard(index=True, excel=True)
    return df_table

def create_table_handler(workbook=None, writer=None, ECONOMY_ID=None, OUTLOOK_BASE_YEAR=None, OUTLOOK_LAST_YEAR=None, 
                 directory_path= '../input_data/macro/'):
    """
    Main function to create the combined table.
    
    Steps:
      1. Loads the macro data (filtering for the chosen years).
      2. Loads the additional datasets via mapping_functions.
      3. Performs cleaning (e.g. removing subtotal rows).
      4. Stores the macro data in the datasets dictionary.
      5. Calls calculate_other_data (a placeholder for future work).
      6. Creates the energy (and macro) table.
    """
    # --- Load macro data ---
    macro_data_file = find_most_recent_file_date_id(
        directory_path=directory_path, 
        filename_part='APEC_GDP_data_', 
        RETURN_DATE_ID=False
    )
    df_macro = pd.read_csv(os.path.join(directory_path, macro_data_file))
    df_macro = df_macro.loc[
        (df_macro.economy_code == ECONOMY_ID) &
        (df_macro.year.isin([OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR]))
    ]
    
    # --- Load additional datasets using mapping_functions ---
    all_model_df_wides_dict = mapping_functions.find_and_load_latest_data_for_all_sources(
        ECONOMY_ID, ['energy', 'emissions_co2', 'emissions_co2e', 'capacity'], WALK=False)
    
    energy_w_subtotals = all_model_df_wides_dict['energy'][1]
    emissions_co2_w_subtotals = all_model_df_wides_dict['emissions_co2'][1]
    emissions_co2e_w_subtotals = all_model_df_wides_dict['emissions_co2e'][1]
    capacity_w_subtotals = all_model_df_wides_dict['capacity'][1]
    datasets = {
        'energy': energy_w_subtotals, 
        'emissions_co2': emissions_co2_w_subtotals,
        'emissions_co2e': emissions_co2e_w_subtotals, 
        'capacity': capacity_w_subtotals
    }
    
    key_cols = ['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 
                'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', 'subtotal_layout', 'subtotal_results']
    OUTLOOK_BASE_YEAR_str = str(OUTLOOK_BASE_YEAR)
    OUTLOOK_LAST_YEAR_str = str(OUTLOOK_LAST_YEAR)
    #if dataset_name is capacity then change key_cols
    
    key_cols_capacity = ['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'sheet']
    # Clean each dataset by keeping only the key columns and the selected years,
    # and remove subtotal rows.
    
    for dataset_name, dataset in datasets.items():
        if dataset_name == 'capacity':
            dataset_hist = dataset[key_cols_capacity + [OUTLOOK_BASE_YEAR_str]]
            dataset_proj = dataset[key_cols_capacity + [OUTLOOK_LAST_YEAR_str]]
        else:
            
            #remove aggregate sector and fuel values:
            dataset = dataset[~dataset['fuels'].isin([
                        '19_total',
                        '20_total_renewables',
                        '21_modern_renewables'
            ])]
            
            dataset_hist = dataset[key_cols + [OUTLOOK_BASE_YEAR_str]]
            dataset_proj = dataset[key_cols + [OUTLOOK_LAST_YEAR_str]]
            
            dataset_hist = dataset_hist[(dataset_hist.subtotal_layout == False)]
            dataset_proj = dataset_proj[(dataset_proj.subtotal_results == False)]
            
        datasets[dataset_name] = pd.concat([dataset_hist, dataset_proj], axis=0).fillna(0)
    
    # Add the macro data.
    datasets['macro'] = df_macro
    
    # --- Placeholder for calculating additional "other" data ---
    calculate_other_data(datasets, ECONOMY_ID, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
    
    # --- Create the energy table (which includes macro rows) ---
    table = create_table(
        datasets=datasets,
        ECONOMY_ID=ECONOMY_ID,
        OUTLOOK_BASE_YEAR=OUTLOOK_BASE_YEAR,
        OUTLOOK_LAST_YEAR=OUTLOOK_LAST_YEAR,
        macro_df=datasets['macro']
    )
    
    if writer is not None:
        # breakpoint()
        # Write table to sheet
        table.to_excel(writer, sheet_name='page_1_table', index=True,  merge_cells=False)    
    return writer, workbook, table

#%%

# # -------------------------------------------------------------------
# # EXAMPLE USAGE
# if __name__ == "__main__":
#     ECONOMY_ID = "09_ROK"          # Example economy code
#     OUTLOOK_BASE_YEAR = 2022       # Base year (or 2021 for 16_RUS)
#     OUTLOOK_LAST_YEAR = 2060       # Target year
#     table = create_table_handler(ECONOMY_ID=ECONOMY_ID, OUTLOOK_BASE_YEAR=OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR=, OUTLOOK_LAST_YEAR)
    