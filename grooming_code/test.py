#first file for the setup of the project
#import data from input_data/model_df_wide_20230420.csv
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

#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')
#read in data
model_df_wide = pd.read_csv('../input_data/model_df_wide_20230420.csv')

#filter for reference scenarios
model_df_wide = model_df_wide[model_df_wide['scenarios'] == 'reference']
#filter for 01_AUS economy
model_df_wide = model_df_wide[model_df_wide['economy'] == '01_AUS']

#data details:
#Columns: model_df_wide.columns
# Index(['scenarios', 'economy', 'sectors', 'sub1sectors', 'sub2sectors',
#        'sub3sectors', 'sub4sectors', 'fuels', 'subfuels', '1980', '1981',
#        '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990',
#        '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999',
#        '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008',
#        '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
#        '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026',
#        '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035',
#        '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043', '2044',
#        '2045', '2046', '2047', '2048', '2049', '2050', '2051', '2052', '2053',
#        '2054', '2055', '2056', '2057', '2058', '2059', '2060', '2061', '2062',
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

# #print unique values for the object columns
# for col in model_df_wide.columns:
#     if model_df_wide[col].dtype == 'object':
#         print(col, model_df_wide[col].unique())

# scenarios ['reference' 'target']
# economy ['01_AUS' '02_BD' '03_CDA' '04_CHL' '05_PRC' '06_HKC' '07_INA' '08_JPN'
#  '09_ROK' '10_MAS' '11_MEX' '12_NZ' '13_PNG' '14_PE' '15_PHL' '16_RUS'
#  '17_SGP' '18_CT' '19_THA' '20_USA' '21_VN' '22_SEA' '23_NEA' '23b_ONEA'
#  '24_OAM' '24b_OOAM' '25_OCE' 'APEC']
# sectors ['01_production' '02_imports' '03_exports'
#  '04_international_marine_bunkers' '05_international_aviation_bunkers'
#  '06_stock_changes' '07_total_primary_energy_supply' '08_transfers'
#  '09_total_transformation_sector' '10_losses_and_own_use'
#  '11_statistical_discrepancy' '12_total_final_consumption'
#  '13_total_final_energy_consumption' '14_industry_sector'
#  '15_transport_sector' '16_other_sector' '17_nonenergy_use'
#  '18_electricity_output_in_gwh' '19_heat_output_in_pj']
# sub1sectors ['x' '09_01_electricity_plants' '09_02_chp_plants' '09_x_heat_plants'
#  '09_06_gas_processing_plants' '09_08_coal_transformation'
#  '09_10_biofuels_processing' '09_13_hydrogen_transformation'
#  '09_07_oil_refineries' '09_12_nonspecified_transformation'
#  '10_01_own_use' '10_02_transmision_and_distribution_losses'
#  '14_01_mining_and_quarrying' '14_02_construction' '14_03_manufacturing'
#  '15_01_domestic_air_transport' '15_02_road' '15_03_rail'
#  '15_04_domestic_navigation' '15_05_pipeline_transport'
#  '15_06_nonspecified_transport' '16_01_buildings'
#  '16_02_agriculture_and_fishing' '16_05_nonspecified_others'
#  '17_01_transformation_sector' '17_02_industry_sector'
#  '17_04_other_sector' '18_01_electricity_plants' '18_02_chp_plants'
#  '19_01_chp_plants' '19_02_heat_plants' '08_03_products_transferred'
#  '08_02_interproduct_transfers' '17_03_transport_sector'
#  '09_09_petrochemical_industry' '09_11_charcoal_processing'
#  '09_05_chemical_heat_for_electricity_production' '09_04_electric_boilers']
# sub2sectors ['x' '09_01_01_coal_power' '09_01_02_gas_power' '09_01_03_oil'
#  '09_01_04_nuclear' '09_01_05_hydro' '09_01_06_biomass'
#  '09_01_07_geothermal' '09_01_08_solar' '09_01_09_wind'
#  '09_01_10_otherrenewable' '09_01_11_otherfuel' '09_01_12_storage'
#  '09_02_01_coal' '09_02_02_gas' '09_02_03_oil' '09_02_04_biomass'
#  '09_x_01_coal' '09_x_02_gas' '09_x_03_oil' '09_x_04_biomass'
#  '09_06_01_gas_works_plants' '09_08_01_coke_ovens'
#  '09_08_02_blast_furnaces' '09_08_03_patent_fuel_plants'
#  '09_08_04_bkb_pb_plants' '09_08_05_liquefaction_coal_to_oil'
#  '09_13_01_electrolysers' '09_13_02_smr_wo_ccs' '09_13_03_smr_w_ccs'
#  '09_13_04_coal_wo_ccs' '09_13_05_coal_w_ccs' '09_13_06_others'
#  '10_01_01_electricity_chp_and_heat_plants'
#  '10_01_03_liquefaction_regasification_plants' '10_01_08_coke_ovens'
#  '10_01_09_coal_mines' '10_01_10_blast_furnaces' '10_01_14_oil_refineries'
#  '10_01_15_oil_and_gas_extraction' '10_01_16_biofuels_processing'
#  '10_01_19_ccs' '10_01_07_gas_separation' '10_01_06_gastoliquids_plants'
#  '10_01_12_bkb_pb_plants' '10_01_18_nonspecified_own_uses'
#  '10_01_02_gas_works_plants' '10_01_13_liquefaction_plants_coal_to_oil'
#  '14_03_01_iron_and_steel' '14_03_02_chemical_incl_petrochemical'
#  '14_03_03_non_ferrous_metals' '14_03_04_nonmetallic_mineral_products'
#  '14_03_05_transportation_equipment' '14_03_06_machinery'
#  '14_03_07_food_beverages_and_tobacco' '14_03_08_pulp_paper_and_printing'
#  '14_03_09_wood_and_wood_products' '14_03_10_textiles_and_leather'
#  '14_03_11_nonspecified_industry' '15_01_01_passenger' '15_01_02_freight'
#  '15_02_01_passenger' '15_02_02_freight' '15_03_01_passenger'
#  '15_03_02_freight' '15_04_01_passenger' '15_04_02_freight'
#  '16_01_01_commercial_and_public_services' '16_01_02_residential'
#  '16_02_03_agriculture' '16_02_04_fishing' '18_01_01_coal_power'
#  '18_01_02_gas_power' '18_01_03_oil' '18_01_04_nuclear' '18_01_05_hydro'
#  '18_01_06_biomass' '18_01_07_geothermal' '18_01_08_solar' '18_01_09_wind'
#  '18_01_10_otherrenewable' '18_01_11_otherfuel' '18_01_12_storage'
#  '18_02_01_coal' '18_02_02_gas' '18_02_03_oil' '18_02_04_biomass'
#  '19_01_01_coal' '19_01_02_gas' '19_01_03_oil' '19_01_04_biomass'
#  '19_02_01_coal' '19_02_02_gas' '19_02_03_oil' '19_02_04_biomass'
#  '09_06_02_liquefaction_regasification_plants'
#  '09_06_03_natural_gas_blending_plants' '09_06_04_gastoliquids_plants'
#  '10_01_05_natural_gas_blending_plants']
# sub3sectors ['x' '09_01_01_01_subcritical' '09_01_01_02_superultracritical'
#  '09_01_01_03_advultracritical' '09_01_01_04_ccs' '09_01_02_01_gasturbine'
#  '09_01_02_02_combinedcycle' '09_01_02_03_ccs' '09_01_05_01_large'
#  '09_01_05_02_mediumsmall' '09_01_05_03_pump' '09_01_08_01_utility'
#  '09_01_08_02_rooftop' '09_01_08_03_csp' '09_01_09_01_onshore'
#  '09_01_09_02_offshore' '14_03_01_01_fs' '14_03_01_02_eaf'
#  '14_03_01_03_ccs' '14_03_01_04_bfbof' '14_03_01_05_hydrogen'
#  '14_03_02_01_fs' '14_03_02_02_ccs' '14_03_04_01_ccs' '14_03_04_02_nonccs'
#  '15_02_01_01_two_wheeler' '15_02_01_02_light_vehicle'
#  '15_02_01_03_light_truck' '15_02_01_04_heavy_truck'
#  '15_02_02_01_two_wheeler' '15_02_02_02_light_vehicle'
#  '15_02_02_03_light_truck' '15_02_02_04_heavy_truck'
#  '18_01_01_01_subcritical' '18_01_01_02_superultracritical'
#  '18_01_01_03_advultracritical' '18_01_01_04_ccs' '18_01_02_01_gasturbine'
#  '18_01_02_02_combinedcycle' '18_01_02_03_ccs' '18_01_05_01_large'
#  '18_01_05_02_mediumsmall' '18_01_05_03_pump' '18_01_08_01_utility'
#  '18_01_08_02_rooftop' '18_01_08_03_csp' '18_01_09_01_onshore'
#  '18_01_09_02_offshore']
# sub4sectors ['x' '15_02_01_01_01_diesel_engine' '15_02_01_01_02_gasoline_engine'
#  '15_02_01_01_03_battery_ev' '15_02_01_01_04_compressed_natual_gas'
#  '15_02_01_01_05_plugin_hybrid_ev_gasoline'
#  '15_02_01_01_06_plugin_hybrid_ev_diesel' '15_02_01_02_01_diesel_engine'
#  '15_02_01_02_02_gasoline_engine' '15_02_01_02_03_battery_ev'
#  '15_02_01_02_04_compressed_natual_gas'
#  '15_02_01_02_05_plugin_hybrid_ev_gasoline'
#  '15_02_01_02_06_plugin_hybrid_ev_diesel' '15_02_01_03_01_diesel_engine'
#  '15_02_01_03_02_gasoline_engine' '15_02_01_03_03_battery_ev'
#  '15_02_01_03_04_compressed_natual_gas'
#  '15_02_01_03_05_plugin_hybrid_ev_gasoline'
#  '15_02_01_03_06_plugin_hybrid_ev_diesel' '15_02_01_04_01_diesel_engine'
#  '15_02_01_04_02_gasoline_engine' '15_02_01_04_03_battery_ev'
#  '15_02_01_04_04_compressed_natual_gas'
#  '15_02_01_04_05_plugin_hybrid_ev_gasoline'
#  '15_02_01_04_06_plugin_hybrid_ev_diesel' '15_02_02_01_01_diesel_engine'
#  '15_02_02_01_02_gasoline_engine' '15_02_02_01_03_battery_ev'
#  '15_02_02_01_04_compressed_natual_gas'
#  '15_02_02_01_05_plugin_hybrid_ev_gasoline'
#  '15_02_02_01_06_plugin_hybrid_ev_diesel' '15_02_02_02_01_diesel_engine'
#  '15_02_02_02_02_gasoline_engine' '15_02_02_02_03_battery_ev'
#  '15_02_02_02_04_compressed_natual_gas'
#  '15_02_02_02_05_plugin_hybrid_ev_gasoline'
#  '15_02_02_02_06_plugin_hybrid_ev_diesel' '15_02_02_03_01_diesel_engine'
#  '15_02_02_03_02_gasoline_engine' '15_02_02_03_03_battery_ev'
#  '15_02_02_03_04_compressed_natual_gas'
#  '15_02_02_03_05_plugin_hybrid_ev_gasoline'
#  '15_02_02_03_06_plugin_hybrid_ev_diesel' '15_02_02_04_01_diesel_engine'
#  '15_02_02_04_02_gasoline_engine' '15_02_02_04_03_battery_ev'
#  '15_02_02_04_04_compressed_natual_gas'
#  '15_02_02_04_05_plugin_hybrid_ev_gasoline'
#  '15_02_02_04_06_plugin_hybrid_ev_diesel']
# fuels ['01_coal' '02_coal_products' '03_peat' '04_peat_products'
#  '05_oil_shale_and_oil_sands' '06_crude_oil_and_ngl'
#  '07_petroleum_products' '08_gas' '09_nuclear' '10_hydro' '11_geothermal'
#  '12_solar' '13_tide_wave_ocean' '14_wind' '15_solid_biomass' '16_others'
#  '17_electricity' '18_heat' '19_total' '20_total_renewables'
#  '21_modern_renewables']
# subfuels ['01_01_coking_coal' '01_x_thermal_coal' '01_05_lignite' 'x'
#  '06_01_crude_oil' '06_02_natural_gas_liquids' '06_x_other_hydrocarbons'
#  '07_01_motor_gasoline' '07_02_aviation_gasoline' '07_03_naphtha'
#  '07_x_jet_fuel' '07_06_kerosene' '07_07_gas_diesel_oil' '07_08_fuel_oil'
#  '07_09_lpg' '07_10_refinery_gas_not_liquefied' '07_11_ethane'
#  '07_x_other_petroleum_products' '08_01_natural_gas' '08_02_lng'
#  '08_03_gas_works_gas' '12_01_of_which_photovoltaics' '12_x_other_solar'
#  '15_01_fuelwood_and_woodwaste' '15_02_bagasse' '15_03_charcoal'
#  '15_04_black_liquor' '15_05_other_biomass' '16_01_biogas'
#  '16_02_industrial_waste' '16_03_municipal_solid_waste_renewable'
#  '16_04_municipal_solid_waste_nonrenewable' '16_05_biogasoline'
#  '16_06_biodiesel' '16_07_bio_jet_kerosene' '16_08_other_liquid_biofuels'
#  '16_09_other_sources' '16_x_ammonia' '16_x_hydrogen']



##############################################################################
#%%
#take in the model_variables.xlsx file and check that the unique variables in the columns in Variables sheet match the variables in the columns in the Data sheet. If not, throw a descriptive error/warning.

model_variables = pd.read_excel('../input_data/model_variables.xlsx', sheet_name='Variables', header = 2)
#drop first 2 rows (includes the columns row) and check the next row is a set of columns that match the object columns in the Data sheet

#we first need to check that the columns in the Variables sheet match the columns in the Data sheet
object_columns = model_df_wide.select_dtypes(include=['object']).columns
#check the difference between the columns in the Variables sheet and the columns in the Data sheet
diff = np.setdiff1d(model_variables.columns, object_columns)

if len(diff) > 0:
    print('The following columns between the Variables sheet and the Data are different: ', diff)
    raise Exception('The columns in the Variables sheet do not match the columns in the Data sheet')

#Now check that the unique variables in the columns in the Variables sheet match the unique variables in the columns in the Data sheet
for col in object_columns:
    unique_variables = model_variables[col].dropna().unique()
    unique_variables.sort()
    unique_variables_data = model_df_wide[col].dropna().unique()
    unique_variables_data.sort()
    diff = np.setdiff1d(unique_variables, unique_variables_data)
    if len(diff) > 0:
        #determine whether its missing from the Variables sheet or the Data sheet
        for variable in diff:
            if variable in unique_variables:
                data_checking_warning_or_error('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
            else:
                data_checking_warning_or_error('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))

##############################################################################


#import mappings:
#these will be mappings from detailed categories to simplified categories which will be shown in the visualisations: 
# Eg: 09_09_petrochemical_industry to Industry

detailed_sector_mappings = pd.read_excel('../input_data/model_variables.xlsx', sheet_name='Sectors', header = 2)
# detailed_sector_mappings.columns: Index(['sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors'], dtype='object')
detailed_fuel_mappings = pd.read_excel('../input_data/model_variables.xlsx', sheet_name='Fuels', header = 2)
# detailed_fuel_mappings.columns: Index(['fuels', 'subfuels'], dtype='object')

simplified_sector_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='simplified_sector')
# simplified_sector_mappings.columns: Index(['sectors_simplified', 'sectors'], dtype='object')
#remove comment col if it is there
if 'comment' in simplified_sector_mappings.columns:
    simplified_sector_mappings = simplified_sector_mappings.drop(columns=['comment'])

simplified_fuel_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='simplified_fuel')
# simplified_fuel_mappings.columns: Index(['fuels_simplified', 'fuels'], dtype='object')
#remove comment col if it is there
if 'comment' in simplified_fuel_mappings.columns:
    simplified_fuel_mappings = simplified_fuel_mappings.drop(columns=['comment'])

transformation_sector_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='transformation_sector_mappings')
# transformation_sector_mappings.columns: Index(['transformation_sectors'	'sub1sectors'], dtype='object')
#remove comment col if it is there
if 'comment' in transformation_sector_mappings.columns:
    transformation_sector_mappings = transformation_sector_mappings.drop(columns=['comment'])

economy_mappings = pd.read_csv('../config/economy_code_to_name.csv')
# economy_mappings.columns: Index(['economy', 'economy_name', 'alt_aperc_code', 'alt_aperc_code2','region1', 'region2_test', 'region3_aperc_code'],dtype='object')

fuels_used_by_modellers = pd.read_excel('../input_data/fuels_used_by_modellers.xlsx', sheet_name='fuels_by_sectors')
#drop first row
fuels_used_by_modellers = fuels_used_by_modellers.drop(0)
# 'FUELS', 'Industry and non-energy', 'Transport', 'Buildings',
#        'Hydrogen', 'Ag, fish & non-spec', 'Power', 'Refining (oil & biofuels)',
#        'Supply', 'Unnamed: 9', 'Industry and non-energy.1', 'Transport.1',
#        'Buildings.1', 'Hydrogen.1', 'Ag, fish & non-spec.1', 'Power.1',
#        'Refining (oil & biofuels).1', 'Supply.1'
###########################
#%%
#for sector and fuel we will join detailed sector mappings with the simplified sector mappings. This will allow for quicker lookups when we want to map from detailed to simplified
#note that detailed sector mappings need to have all but the last of the columns forward filled from the top. for example the first row in first column may have category X. but then for the next 4 rows the field is NA. This means that the category X is valid for the next 4 rows. So we need to forward fill the NA values with X. 

#However there is one caveat: in the detailed_sector_mappings, where a more specified category is being filled down, but then the next row is for a different, less specific category than the proveiouis one. Its hard to explain but the following code should make it clear.
#first, fill any NA's in sub4sectors with 'x'
detailed_sector_mappings['sub4sectors'] = detailed_sector_mappings['sub4sectors'].fillna('x')
#now fill any na's in sub3sectors with 'x' IF the next row in sub4sectors is 'x'
detailed_sector_mappings['sub3sectors'] = np.where((detailed_sector_mappings['sub4sectors'] == 'x') & (detailed_sector_mappings['sub3sectors'].isna()), 'x', detailed_sector_mappings['sub3sectors'])
#now fill any na's in sub2sectors with 'x' IF the next row in sub3sectors is 'x'
detailed_sector_mappings['sub2sectors'] = np.where((detailed_sector_mappings['sub3sectors'] == 'x') & (detailed_sector_mappings['sub2sectors'].isna()), 'x', detailed_sector_mappings['sub2sectors'])
#now fill any na's in sub1sectors with 'x' IF the next row in sub2sectors is 'x'
detailed_sector_mappings['sub1sectors'] = np.where((detailed_sector_mappings['sub2sectors'] == 'x') & (detailed_sector_mappings['sub1sectors'].isna()), 'x', detailed_sector_mappings['sub1sectors'])
#now we can ffill remainign missing values
detailed_sector_mappings['sectors'] = detailed_sector_mappings['sectors'].fillna(method='ffill')
detailed_sector_mappings['sub1sectors'] = detailed_sector_mappings['sub1sectors'].fillna(method='ffill')
detailed_sector_mappings['sub2sectors'] = detailed_sector_mappings['sub2sectors'].fillna(method='ffill')
detailed_sector_mappings['sub3sectors'] = detailed_sector_mappings['sub3sectors'].fillna(method='ffill')
#and replace any remaining 'x' with NA
detailed_sector_mappings = detailed_sector_mappings.replace('x', np.nan)

#now we dont need to do the same for fuels:
detailed_fuel_mappings['fuels'] = detailed_fuel_mappings['fuels'].fillna(method='ffill')

#now join the detailed and simplified mappings:
fuel_mappings = pd.merge(simplified_fuel_mappings,detailed_fuel_mappings, how='outer', on='fuels')
transformation_sector_mappings = pd.merge(transformation_sector_mappings,detailed_sector_mappings.drop(['sectors'], axis=1), how='left', on='sub1sectors')
#%%
#############################
#for sector mappings we need to do it a bit differently. First we will melt the simplified_sector_mappings so that we have a column for the detailed_sectors values and a column for the sectors_simplified values. There will also be a column to indicate what column the detailed sectors values are from
#so do a melt:
simplified_sector_mappings = pd.melt(simplified_sector_mappings, id_vars=['sectors_simplified'], var_name='column_name', value_name='detailed_sectors')
#now we need to remove the rows where the detailed_sectors are NA. This is because we only want to map the detailed_sectors that have a mapping to a simplified_sector
simplified_sector_mappings = simplified_sector_mappings.dropna(subset=['detailed_sectors'])
#and now loop through the rows in the dataframe, find the column in the column_name column and then map the detailed_sectors to the sectors_simplified so the simplified sectors column vlaues are populated
sector_mappings = detailed_sector_mappings.copy()
#%%
for index, row in simplified_sector_mappings.iterrows():

    column_name = row['column_name']
    detailed_sector = row['detailed_sectors']
    simplified_sector = row['sectors_simplified']   

    #now find those rows in the detailed_sector_mappings where the column is the same as the column_name and the value is equal to detailed_sector. Then set the simplified sector col to simplified_sector
    sector_mappings.loc[(sector_mappings[column_name] == detailed_sector), 'sectors_simplified'] = simplified_sector

#melt the sector_mappings so that we have a column for the detailed_sectors values and a column for the sectors_simplified values. There will also be a column to indicate what column the detailed sectors values are from
sector_mappings = pd.melt(sector_mappings, id_vars=['sectors_simplified'], var_name='column_name', value_name='detailed_sectors')
#drop nas
sector_mappings = sector_mappings.dropna(subset=['detailed_sectors'])
#drop duplicates
sector_mappings = sector_mappings.drop_duplicates(subset=['detailed_sectors'])
#save in intermediate data
sector_mappings.to_csv(f'../intermediate_data/config/sector_mappings_{FILE_DATE_ID}.csv', index=False)

#%%
#############################

#check for nas in the simplified columns. this indicates that the simplified column is missing a mapping 
nas = sector_mappings['sectors_simplified'].isna()
if nas.any():
    data_checking_warning_or_error('The following sectors_simplified are missing a mapping: {}'.format(sector_mappings['sectors'][nas].unique()))
nas = fuel_mappings['fuels_simplified'].isna()
if nas.any():
    data_checking_warning_or_error('The following fuels_simplified are missing a mapping: {}'.format(fuel_mappings['fuels'][nas].unique()))

#save in intermediate data
sector_mappings.to_csv(f'../intermediate_data/config/sector_mappings_{FILE_DATE_ID}.csv', index=False)
fuel_mappings.to_csv(f'../intermediate_data/config/fuel_mappings_{FILE_DATE_ID}.csv', index=False)
transformation_sector_mappings.to_csv(f'../intermediate_data/config/transformation_sector_mappings_{FILE_DATE_ID}.csv', index=False)
#%%
#################################
#for economy and region mappings we have a few options. But generally wee are going to wwant to convert data from economy or alt_aperc_code to one of the other columns, especially one of economy_name, region1 or region2_test.
##############################################################################
#%%
#now we will take in the 8th edition outlook data and charts workbook and copy the categories used for each sheet into a dataframe. This will be used as the basis for which to plot the data in the 9th edition. i.e. we will create a function that will plot specified graphs for each sheet using the categories in the dataframe for that sheet. 
#This will mean that we will ahve to identify the categories in the 9th edition workbook and then map them to the categories in the 8th edition workbook. 
# D:\APERC\9th_edition_visualisation\input_data\01_AUS_charts_2022-07-14-1530.xlsx
example_workbook = pd.ExcelFile(f'../input_data/01_AUS_charts_2022-07-14-1530.xlsx')
tables_dict = {}
#loop through the worksheets and extract the categories
sheets = example_workbook.sheet_names
for sheet in sheets:
    #load in the sheet
    df = pd.read_excel(example_workbook, sheet_name=sheet, header=None)
    #identify where the data is. 
    #first extract the unit from the 2nd row. e.g. Units: Petajoules means that Unit is Petajoules
    try:
        unit = df.iloc[1,0].split(':')[1].strip()
    except:
        unit = np.nan
    #now extract the data. Do this by looking for Non NAN's in the 5th column. Then where there is a non NAN, identify if it is a 4 digit number between 2000 and 2050. this means it is a year. 
    #Then define the column range as being first column in that row, to the final year in that row.
    #Then define the row range as being the first row with a non NAN in the 5th column, until the next row with a NAN in the 5th column.
    #note that this is only one of a few tables in that sheet. We will put this table as a dataframe into a list in a dictionary with the sheet name as the key. Later we will combine everything in the dictionary

    #first identify the rows and columns to extract

    #identify the rows
    #first identify the rows where there is a non NAN in the 5th column
    column_name_rows = df[df.iloc[:,4].notna()].index
    #now identify the rows where the value in the 5th column is a 4 digit number between 2000 and 2050. Note that we have to convert the values to strings to do this
    string_values = df.iloc[:,4].astype(str)
    #Grab rows where string is numeric or a float
    string_values = string_values[string_values.str.isnumeric() | string_values.str.contains('\.')]
    #remove any .0's
    string_values = string_values.str.replace('\.0','')
    #remove any rows where there is still a . in the string
    string_values = string_values[~string_values.str.contains('\.')]
    #Grab rows where the string length is 4 and between 2000 and 2050
    string_values = string_values[(string_values.str.len() == 4)]
    column_name_rows = string_values[(string_values.astype(int) >= 2000) & (string_values.astype(int) <= 2050)].index

    #make unit the first entry in the dicts list
    tables_dict[sheet] = [unit]

    #now identify the first and last row for each table
    for table_columns in column_name_rows:
        table = df.iloc[table_columns:,:]
        #reset the index so that the first row is 0
        table = table.reset_index(drop=True)
        #now identify the first row with a NAN in the 5th column (if there is one)
        if table.iloc[:,4].isna().any():
            table_final_row = table[table.iloc[:,4].isna()].index[0]
        else:#use the last row
            table_final_row = table.shape[0]
        #now identify the last column as the first NAN in the first row (if there is one)
        if table.iloc[0,:].isna().any():
            table_final_column = table.iloc[0,:][table.iloc[0,:].isna()].index[0]
        else:#use the last column
            table_final_column = table.shape[1]
        #now extract the table
        table = table.iloc[:table_final_row, :table_final_column]
        #now set the column names as the first row
        table.columns = table.iloc[0,:]
        #drop the first row
        table = table.iloc[1:,:]
        #make the years into strings and remove any .0's
        table.columns = table.columns.astype(str).str.replace('\.0','')
        #now put the table into the dictionary
        tables_dict[sheet].append(table)

#%%
#now go through the dictionary and combine the tables into groups of dataframes based on the column names.
#we will remove the years because tehy are not useful for this purpose
table_tuple = ()
#table_tuple is a tuple of dataframes. Each dataframe is a group of tables that have the same column names and an extra column which is the sheet name

for sheet in tables_dict.keys():
    #skip the first entry in the list because that is the unit
    unit = tables_dict[sheet][0]
    table_number = 0
    for table in tables_dict[sheet][1:]:
        TABLE_FOUND = False
        table_number = table_number + 1
        #now remove any columns that are years (4 digit numbers between 2000 and 2050)
        table = table.drop(columns=table.columns[(table.columns.str.isnumeric()) & (table.columns.str.len() == 4)])                           

        #add the sheet name as a column
        table['sheet'] = sheet
        #add the unit as a column
        table['unit'] = unit
        #add the table number as a column
        table['table_number'] = table_number

        #first identify the column names
        column_names = table.columns
        #now loop through the tables in table_tuple and identify if the column names all exist in a single table. If they do, then add concat the table to that group
        for i,table_group in enumerate(table_tuple):
            if all(column_name in table_group.columns for column_name in column_names):
                table_group = pd.concat([table_group, table]).drop_duplicates()
                #now add the table_group back into the tuple
                table_tuple = table_tuple[:i] + (table_group,) + table_tuple[i+1:]
                TABLE_FOUND = True
                break
        if TABLE_FOUND == False:
            #add a new table!
            table_tuple = table_tuple + (table,)
    
#now we have a tuple of dataframes. Each dataframe is a group of tables that have the same column names and an extra column which is the sheet name
#we now can go through them manually and identify any patterns or perhaps where the column is based on a mapping we have but with a different name. In the end we want to be able to use this as an input to plot a whole bunch of graphs.

#now we will manually adjust any values that we know can (and need) to be changed to a more descriptive value that works weith the mappings. For example: 
#where the sheet is Power fuel consumption then change the column Transformation so that the value Input fuel is now Power

###############
#%%
#save to a workbook so we can look at it. no need for file_date_id because the input data is constant
with pd.ExcelWriter('../intermediate_data/config/charts_mapping_8th.xlsx') as writer:
    for i, table_group in enumerate(table_tuple):
        table_group.to_excel(writer, sheet_name=str(i), index=False)
    
# %%
####################################
#mapping the 9th edition data to 8th edition data for the charts:
#now we will attempt to map the tables to the model data so we can plot them
#the data is in model_df_wide which was loaded earlier
#first we should conver the fuels in model_df_wide to the simplified fuel names using fuel_mappings
#drop uneeded columns and then sum by the object cols
model_df_wide_mapped_8th = model_df_wide.drop(columns=['sub2sectors', 'sub3sectors', 'sub4sectors', 'subfuels'])
object_cols = model_df_wide_mapped_8th.select_dtypes(include='object').columns.tolist()
model_df_wide_mapped_8th = model_df_wide_mapped_8th.groupby(object_cols).sum().reset_index()
#merge fuels
model_df_wide_mapped_8th = model_df_wide_mapped_8th.merge(fuel_mappings[['fuels_simplified', 'fuels']], how='left', on='fuels')
#now do sectors
model_df_wide_mapped_8th = model_df_wide_mapped_8th.merge(sector_mappings[['sectors_simplified', 'sectors']], how='left', on='sectors')
#merge transformastion sectors
model_df_wide_mapped_8th = model_df_wide_mapped_8th.merge(transformation_sector_mappings[['transformation_sectors', 'sub1sectors']], how='left', on='sub1sectors')
#now get the cols that are objects and make them at the front of the dataframe
object_cols = model_df_wide_mapped_8th.select_dtypes(include='object').columns.tolist()
model_df_wide_mapped_8th = model_df_wide_mapped_8th[object_cols + [col for col in model_df_wide_mapped_8th.columns if col not in object_cols]]

#now we need to map the model data to the tables in the table_tuple. Unfortunately the column names in the table tuple dont indicate very well what the category is. So we will instead search for that category in a set of the unique categories in model_df_wide_mapped_8th
unique_categories = model_df_wide_mapped_8th[object_cols].drop_duplicates().reset_index(drop=True)
#%%
#######################
#new version of the above. attempting to change the values in the columns instead of the column names
#first manually change some of the column names to make them easier to work with. this will help prevent mixing up fuel values with sector values etc
column_changes_dict = {}
column_changes_dict['FUEL'] = 'fuels'
column_changes_dict['Fuel'] = 'fuels'
column_changes_dict['fuel_code'] = 'fuels'
column_changes_dict['item_code_new'] = 'sectors'
column_changes_dict['Transformation'] = 'sectors'
column_changes_dict['Generation'] = 'sectors'
column_changes_dict['Sector'] = 'sectors'
column_changes_dict['TECHNOLOGY'] = 'sectors'
column_changes_dict['Technology'] = 'sectors'

#now change the columns
table_tuple_columns_mapped = ()
for table_group in table_tuple:

    #there is one example where we cannot use column_changes_dict because the column name TECHNOLOGY refers to fuel and Generation is the sector. So if both these columns exist we will change the TECHNOLOGY column to fuels
    if 'TECHNOLOGY' in table_group.columns and 'Generation' in table_group.columns:
        table_group = table_group.rename(columns={'TECHNOLOGY':'fuels'})
        table_group = table_group.rename(columns={'Generation':'sectors'})
    else:
        #change cols according to column_changes_dict
        table_group = table_group.rename(columns=column_changes_dict)
    #and create a new column called 'COLUMN_mapped' for each column except the excludeable_cols, but make it empty
    for col in table_group.columns:
        if col in excludeable_cols:
            continue
        table_group[col + '_mapped'] = np.nan
    #now add the table_group to the tuple
    table_tuple_columns_mapped = table_tuple_columns_mapped + (table_group,)

#now using this we can loop through the table and try to map the values to the model data. However, because our goal is to try create a config file which states the graphs we want to create and their inputs, we wont replace the values, instead we will create new columns with the mapped values. The column will be named COLUMN_mapped where COLUMN is the original column name. if the mapping was not done or is incorrect we will change it manually.
#based on if the column is a fuels or sectors column we will look in different cols for the mapping. The mapping will be: fuels_simplified -> fuels (e.g if the value is in fuels_simplified then the value put in COLUMN_mapped will be the corresponding value in fuels. Same for sectors. But then also the mapping is sub1sectors -> sub1sectors and sectors -> sectors. This is because this is accurate as we need anyway (likewise for fuels -> fuels)
#actually we are trying sectors -> sectors_simplified and fuels -> fuels_simplified
mapping_columns_dict = {}
mapping_columns_dict['fuels_simplified'] = 'fuels_simplified'
mapping_columns_dict['sectors_simplified'] = 'sectors_simplified'
mapping_columns_dict['sub1sectors'] = 'sub1sectors'
mapping_columns_dict['sectors'] = 'sectors_simplified'
mapping_columns_dict['fuels'] = 'fuels_simplified'

#note that we wil only be mapping values if they are in a fuel or sectors column. we will not be mapping values in other columns. 
table_tuple_values_mapped = ()
for table_group in table_tuple_columns_mapped:
    for col in table_group.columns:
        if col =='sectors':
            mapping_cols = ['sectors_simplified','sectors', 'sub1sectors']
        elif col == 'fuels':
            mapping_cols = ['fuels_simplified','fuels']
        else:
            continue
        #now loop through the values in the column and try to map them. 
        for value in table_group[col].dropna().unique():
            #now find if it is in any of the columns in unique_categories
            for mapping_col in mapping_cols:
                if value in unique_categories[mapping_col].tolist():
                    #grab the value and its corresponding value, depnding on the column
                    new_value_col = mapping_columns_dict[mapping_col]
                    new_values = unique_categories.loc[unique_categories[mapping_col] == value, new_value_col]
                    #mkae sure there is not more than one unique value availble
                    new_values = new_values.drop_duplicates()
                    if new_values.shape[0] > 1:
                        data_checking_warning_or_error('More than one value found for: ' + value + ' in column: ' + col +' the values are: ' + str(new_values.tolist()) + ' . Please check the data and fix this issue.')
                        continue
                    new_value = new_values.iloc[0]
                    #now replace the value in the column with the new value
                    table_group.loc[table_group[col] == value, col + '_mapped'] = new_value
                    break
    #now add the table_group to the tuple
    table_tuple_values_mapped = table_tuple_values_mapped + (table_group,)

#now we have a tuple of tables with the values mapped. We can now use this to create the config file more easily as we already know what the actual values are for a lot of the columns.

#we will also pull in the mappings from 8th_name_to_9th_name in visualisation_config.xlsx and map from the 8th edition names to the 9th edition names that were manually stated there. This is useful for the names like 'Buildings' which is not a simplified sector

#%%
#we will save the data again in a new file:
#save the data
with pd.ExcelWriter('../intermediate_data/config/charts_mapping_9th_computer_generated.xlsx') as writer:
    for i, table_group in enumerate(table_tuple_values_mapped):
        table_group.to_excel(writer, sheet_name=str(i), index=False)


#%%

#next step will include creating new datasets which create aggregations of data to match some of the categories plotted in the 8th edition. 
#%%






#ok so what this has shown is that some mappings within the data will need to be done based on what their subsectors are. For example, to identify that the transformation sector is for 'power' then we need to know the subsector is a power one and then that the sector is transformation. Then the same for hydorgen (transformation, hydrogen) and refining (transformation, everything else).
#done that above now.

##################################

#make some quick mappings using the sheet 8th_name_to_9th_name in the config folder visualisation_category_mappings.xlsx
#first load in the sheet
sheet_8th_name_to_9th_name = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='8th_name_to_9th_name')
#the sheet ahs cols 8th_name	9th_name	new_col_name	comment
#find the vlaue in 8th name and then find the corresponding value in 9th name which is in the new_col_name col (eg. sector). Then rename the value to the 9th name
new_table_tuple_columns_mapped = ()
for table_group in table_tuple_columns_mapped:
    #for col in table_group.columns except the excludeable_cols
    for col in table_group.columns:
        if col in excludeable_cols:
            continue
        #extract the values in the column that are in the 8th name col. Then rename them to the 9th name col iteratively, and print the change
        for x in table_group[col].unique():
            if x in sheet_8th_name_to_9th_name['8th_name'].tolist():
                table_group[col] = table_group[col].replace(x, sheet_8th_name_to_9th_name[sheet_8th_name_to_9th_name['8th_name'] == x]['9th_name'].iloc[0])
                print('Changed value: ' + x + ' to: ' + sheet_8th_name_to_9th_name[sheet_8th_name_to_9th_name['8th_name'] == x]['9th_name'].iloc[0] + ' in column: ' + col)

    #now add the table_group to the tuple
    new_table_tuple_columns_mapped = new_table_tuple_columns_mapped + (table_group,)

##################################

#%%
#now search the tables within table tuple for unique sheets+table_number combinations that have all their columns and the values in that column in the model data (excluding the sheet, unit and table_number columns). These are the tables that we can plot now!
#first we should get the unique sheets and table_numbers


#Couldnt find value: Real economic output (2018 USD PPP) , from column: Series
# Couldnt find value: Steel , from column: Industry
# Couldnt find value: CCS fossil , from column: tech_mix
# Couldnt find value: Road , from column: Transport
# Couldnt find value: Bus , from column: modality
# Couldnt find value: Input fuel , from column: Transformation
# Couldnt find value: Power , from column: Sector
# Couldnt find value: Own-use and losses , from column: Sector
# Couldnt find value: Thermal coal , from column: fuel_code
# Couldnt find value: Pipeline , from column: Imports
# Couldnt find value: LNG , from column: Exports
# Couldnt find value: Hydrogen , from column: Fuel
# Couldnt find value: Coal gasification CCS , from column: Technology
# Couldnt find value: Input fuel , from column: TECHNOLOGY

#%%
#now plot. 
#essentially what we've done is mapped matts (8th edition, matt was author) plots to our data so that we can programmatically plot them. However there are many missing data points, so we have a bit of work in terms of working out what data is missing vs what just needs to be mapped. in this process it will be important to avoid fixing these issues just to get the plots to work. Instead we should fix the issues so that it will help in the end goal of plotting things for the 9th edition.

#we will take in the table_tuple_columns_mapped and find where we do have data for sheet table_number pairs.
#first join sheet and table_number
for i, table_group in enumerate(table_tuple_columns_mapped):
    table_group['sheet_table_number'] = table_group['sheet'] + table_group['table_number'].astype(str)
    #drop the sheet and table_number columns
    table_tuple_columns_mapped[i] = table_group.drop(columns=['sheet', 'table_number'])

#now we will loop through the table_tuple_columns_mapped and find where we do have data for sheet table_number pairs.
