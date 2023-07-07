#%%
#below is a set of old specifications for the mappings. we will move these to a csv file and import them in the future
# FED and TPES: vectors for impending df builds

# Fuelsa

First_level_fuels = ['1_coal', '2_coal_products', '5_oil_shale_and_oil_sands', '6_crude_oil_and_ngl', '7_petroleum_products',
                     '8_gas', '9_nuclear', '10_hydro', '11_geothermal', '12_solar', '13_tide_wave_ocean', '14_wind', '15_solid_biomass',
                     '16_others', '17_electricity', '18_heat', '19_total', '20_total_renewables', '21_modern_renewables']

Required_fuels = ['1_coal', '2_coal_products', '5_oil_shale_and_oil_sands', '6_crude_oil_and_ngl', '7_petroleum_products',
                  '8_gas', '9_nuclear', '10_hydro', '11_geothermal', '12_solar', '13_tide_wave_ocean', '14_wind', '15_solid_biomass',
                  '16_1_biogas', '16_2_industrial_waste', '16_3_municipal_solid_waste_renewable', '16_4_municipal_solid_waste_nonrenewable',
                  '16_5_biogasoline', '16_6_biodiesel', '16_7_bio_jet_kerosene', '16_8_other_liquid_biofuels', '16_9_other_sources',
                  '16_x_hydrogen', '17_electricity', '18_heat', '19_total', '20_total_renewables', '21_modern_renewables']

required_fuels_elec = ['1_coal', '1_5_lignite', '2_coal_products', '6_crude_oil_and_ngl', '7_petroleum_products', 
                       '8_gas', '9_nuclear', '10_hydro', '11_geothermal', '12_solar', '13_tide_wave_ocean', '14_wind', 
                       '15_solid_biomass', '16_others', '18_heat']

required_fuels_heat = ['1_coal', '1_5_lignite', '2_coal_products', '6_crude_oil_and_ngl', '7_petroleum_products', 
                       '8_gas', '9_nuclear', '11_geothermal', '15_solid_biomass', '16_1_biogas', '16_2_industrial_waste',
                       '16_3_municipal_solid_waste_renewable', '16_4_municipal_solid_waste_nonrenewable', '16_8_other_liquid_biofuels',
                       '16_9_other_sources', '17_electricity', '18_heat']

required_power_input = ['1_coal', '1_5_lignite', '2_coal_products', '6_crude_oil_and_ngl', '7_petroleum_products', 
                        '8_gas', '9_nuclear', '10_hydro', '11_geothermal', '12_solar', '13_tide_wave_ocean', '14_wind', '15_solid_biomass', 
                        '16_1_biogas', '16_2_industrial_waste', '16_3_municipal_solid_waste_renewable', '16_4_municipal_solid_waste_nonrenewable', 
                        '16_6_biodiesel', '16_8_other_liquid_biofuels', '16_9_other_sources']

required_ol_input = ['1_coal', '1_5_lignite', '2_coal_products', '3_peat', '4_peat_products', '6_crude_oil_and_ngl', 
                     '7_petroleum_products', '8_gas', '15_solid_biomass', '16_1_biogas', '16_2_industrial_waste',  
                     '16_6_biodiesel', '17_electricity', '18_heat']#ol means own use and losses

Coal_fuels = ['1_coal', '2_coal_products', '3_peat', '4_peat_products']

Oil_fuels = ['6_crude_oil_and_ngl', '7_petroleum_products', '5_oil_shale_and_oil_sands']

Other_fuels_FED = ['9_nuclear', '16_2_industrial_waste', '16_4_municipal_solid_waste_nonrenewable']

Other_fuels_TPES = ['16_2_industrial_waste', '16_4_municipal_solid_waste_nonrenewable', '16_9_other_sources']

Other_fuels_industry = ['9_nuclear', '10_hydro', '11_geothermal', '12_solar', '13_tide_wave_ocean', '14_wind', '16_1_biogas',
                         '16_2_industrial_waste', '16_3_municipal_solid_waste_renewable', '16_4_municipal_solid_waste_nonrenewable', 
                         '16_5_biogasoline', '16_6_biodiesel', '16_7_bio_jet_kerosene', '16_8_other_liquid_biofuels']

Renewables_fuels = ['10_hydro', '11_geothermal', '12_solar', '13_tide_wave_ocean', '14_wind', '15_solid_biomass', '16_1_biogas', 
                    '16_3_municipal_solid_waste_renewable', '16_5_biogasoline', '16_6_biodiesel', '16_7_bio_jet_kerosene', 
                    '16_8_other_liquid_biofuels']

Renewables_fuels_nobiomass = ['10_hydro', '11_geothermal', '12_solar', '13_tide_wave_ocean', '14_wind', '16_1_biogas', 
                          '16_3_municipal_solid_waste_renewable', '16_5_biogasoline', '16_6_biodiesel', '16_7_bio_jet_kerosene', 
                          '16_8_other_liquid_biofuels']

Petroleum_fuels = ['7_petroleum_products', '7_1_motor_gasoline', '7_2_aviation_gasoline', '7_3_naphtha', '7_4_gasoline_type_jet_fuel',
                   '7_5_kerosene_type_jet_fuel', '7_6_kerosene', '7_7_gas_diesel_oil', '7_8_fuel_oil', '7_9_lpg',
                   '7_10_refinery_gas_not_liquefied', '7_11_ethane', '7_x_other_petroleum_products', '7_12_white_spirit_sbp',
                   '7_13_lubricants', '7_14_bitumen', '7_15_paraffin_waxes', '7_16_petroleum_coke', '7_17_other_products']

marine_bunker_fuels = ['7_7_gas_diesel_oil', '7_8_fuel_oil', '8_1_natural_gas', '16_x_hydrogen', '16_6_biodiesel']
aviation_bunker_fuels = ['7_x_jet_fuel', '16_x_hydrogen', '16_7_bio_jet_kerosene', '7_2_aviation_gasoline']

### Transport fuel vectors

Transport_fuels = ['1_1_coking_coal', '1_5_lignite', '1_x_coal_thermal', '2_coal_products', '7_1_motor_gasoline', '7_2_aviation_gasoline',
                   '7_x_jet_fuel', '7_7_gas_diesel_oil', '7_8_fuel_oil', '7_9_lpg',
                   '7_x_other_petroleum_products', '8_1_natural_gas', '16_5_biogasoline', '16_6_biodiesel',
                   '16_7_bio_jet_kerosene', '16_8_other_liquid_biofuels', '16_x_hydrogen', '17_electricity'] 

Renew_fuel = ['16_5_biogasoline', '16_6_biodiesel', '16_7_bio_jet_kerosene', '16_8_other_liquid_biofuels']

Other_fuel_trans = ['7_8_fuel_oil', '1_1_coking_coal', '1_5_lignite', '1_x_coal_thermal', '2_coal_products', '7_x_other_petroleum_products']

# FED and TPES: Sectors

trad_bio_sectors = ['16_1_commercial_and_public_services', '16_2_residential',
                  '16_3_agriculture', '16_4_fishing', '16_5_nonspecified_others']#trad_bio refers to the UN classficiation of traditional biomass

no_trad_bio_sectors = ['14_industry_sector', '15_transport_sector', '17_nonenergy_use']

Sectors_tfc = ['14_industry_sector', '15_transport_sector', '16_1_commercial_and_public_services', '16_2_residential',
               '16_3_agriculture', '16_4_fishing', '16_5_nonspecified_others', '17_nonenergy_use']

Buildings_items = ['16_1_commercial_and_public_services', '16_2_residential']

Ag_items = ['16_3_agriculture', '16_4_fishing']

Subindustry = ['14_industry_sector', '14_1_iron_and_steel', '14_2_chemical_incl_petrochemical', '14_3_non_ferrous_metals',
               '14_4_nonmetallic_mineral_products', '14_5_transportation_equipment', '14_6_machinery', '14_7_mining_and_quarrying',
               '14_8_food_beverages_and_tobacco', '14_9_pulp_paper_and_printing', '14_10_wood_and_wood_products', 
               '14_11_construction', '14_12_textiles_and_leather', '14_13_nonspecified_industry']

Other_industry = ['14_5_transportation_equipment', '14_6_machinery', '14_8_food_beverages_and_tobacco', '14_10_wood_and_wood_products',
                  '14_11_construction', '14_12_textiles_and_leather']

Transport_modal = ['15_1_domestic_air_transport', '15_2_road', '15_3_rail', '15_4_domestic_navigation', '15_5_pipeline_transport',
                   '15_6_nonspecified_transport']

tpes_items = ['1_indigenous_production', '2_imports', '3_exports', '4_international_marine_bunkers', '5_international_aviation_bunkers',
              '6_stock_change', '7_total_primary_energy_supply']

Prod_items = tpes_items[:1]

# Single fuel vectors

fuel_vector_1 = ['1_indigenous_production', '2_imports', '3_exports', '4_international_marine_bunkers', '5_international_aviation_bunkers',
                 '6_stock_change', '7_total_primary_energy_supply']

fuel_vector_ref = ['2_imports', '3_exports', '4_international_marine_bunkers', '5_international_aviation_bunkers',
                   '6_stock_change', '7_total_primary_energy_supply']

fuel_final_nobunk = ['Production', 'Imports', 'Exports', 'Stock change', 'Total primary energy supply']#bunk refers to bunkers
fuel_final_bunk = ['Production', 'Imports', 'Exports', 'Bunkers', 'Stock change', 'Total primary energy supply']
fuel_final_ref = ['Domestic refining', 'Imports', 'Exports', 'Bunkers', 'Stock change', 'Total primary energy supply']#ref refers to the reference scenario i think

fuel_vector_3 = ['9_1_main_activity_producer', '9_2_autoproducers', '10_losses_and_own_use', '14_industry_sector',
                 '15_transport_sector', '16_1_commercial_and_public_services', '16_2_residential', '16_3_agriculture',
                 '16_4_fishing', '16_5_nonspecified_others', '17_nonenergy_use']

##################################################################################
# Emissions

# Subsets for impending emissions df builds

First_level_emiss = ['1_coal', '2_coal_products', '6_crude_oil_and_ngl', '7_petroleum_products',
                     '8_gas', '16_others', '17_electricity', '18_heat', '19_total']

Required_emiss = ['1_coal', '2_coal_products', '6_crude_oil_and_ngl', '7_petroleum_products',
                  '8_gas', '16_2_industrial_waste', '16_4_municipal_solid_waste_nonrenewable', '16_9_other_sources',
                  '17_electricity', '18_heat', '19_total']

Coal_emiss = ['1_coal', '2_coal_products', '3_peat', '4_peat_products']

Oil_emiss = ['6_crude_oil_and_ngl', '7_petroleum_products']

Heat_others_emiss = ['16_2_industrial_waste', '16_4_municipal_solid_waste_nonrenewable', '16_9_other_sources', '18_heat']

# Emissions sectors (DEMANDS)

Sectors_emiss = ['9_x_power', '10_losses_and_own_use', 
               '14_industry_sector', '15_transport_sector', '16_1_commercial_and_public_services', '16_2_residential',
               '16_3_agriculture', '16_4_fishing', '16_5_nonspecified_others', '17_nonenergy_use']

Buildings_emiss = ['16_1_commercial_and_public_services', '16_2_residential']

Ag_emiss = ['16_3_agriculture', '16_4_fishing']

# FED aggregate fuels

Emissions_agg_fuels = ['Coal', 'Oil', 'Gas', 'Electricity', 'Heat & others']

Emissions_agg_sectors = ['Power', 'Own use', 'Industry', 'Transport', 'Buildings', 'Agriculture', 'Non-specified']

##############################################################################################################################
# TRANSFORMATION vectors for df builds

# FUEL aggregations for UseByTechnology (input fuels)

# First aggregation (13 fuels)
coal_fuel_1 = ['1_x_coal_thermal', '2_coal_products']
lignite_fuel_1 = ['1_5_lignite']
oil_fuel_1 = ['7_7_gas_diesel_oil','7_3_naphtha', '7_8_fuel_oil', '6_1_crude_oil', '7_9_lpg', '7_10_refinery_gas_not_liquefied', '7_x_other_petroleum_products']
gas_fuel_1 = ['8_1_natural_gas']
nuclear_fuel_1 = ['9_nuclear']
hydro_fuel_1 = ['10_hydro']
solar_fuel_1 = ['12_1_of_which_photovoltaics']
wind_fuel_1 = ['14_wind']
biomass_fuel_1 = ['15_1_fuelwood_and_woodwaste', '15_2_bagasse', '15_4_black_liquor', '15_5_other_biomass']
geothermal_fuel_1 = ['11_geothermal']
other_renew_fuel_1 = ['13_tide_wave_ocean', '16_3_municipal_solid_waste_renewable', '16_1_biogas']
other_fuel_1 = ['16_4_municipal_solid_waste_nonrenewable', '16_x_hydrogen', '16_2_industrial_waste']

# '17_electricity', '18_heat'

imports_fuel_1 = ['17_electricity_export']

# Second aggreagtion: Oil, Gas, Nuclear, Imports, Other from above and below two new aggregations (7 fuels)
coal_fuel_2 = ['1_x_coal_thermal', '1_5_lignite', '2_coal_products']
renewables_fuel_2 = ['10_hydro', '11_geothermal', '12_1_of_which_photovoltaics', '13_tide_wave_ocean', '14_wind', '15_1_fuelwood_and_woodwaste', 
                     '15_2_bagasse', '15_4_black_liquor', '15_5_other_biomass', '16_1_biogas', '16_3_municipal_solid_waste_renewable']

# For heat
waste_fuel = ['16_2_industrial_waste', '16_3_municipal_solid_waste_renewable', '16_4_municipal_solid_waste_nonrenewable']

# Own use fuels
coal_ou = ['1_x_coal_thermal', '1_5_lignite', '2_coal_products', '1_1_coking_coal']
oil_ou = ['6_1_crude_oil', '6_x_ngls', '7_1_motor_gasoline', '7_2_aviation_gasoline', '7_3_naphtha', '7_6_kerosene',
          '7_7_gas_diesel_oil', '7_8_fuel_oil', '7_9_lpg', '7_10_refinery_gas_not_liquefied', '7_11_ethane',
          '7_x_jet_fuel', '7_x_other_petroleum_products']
gas_ou = ['8_1_natural_gas']
renew_ou = ['15_1_fuelwood_and_woodwaste', '15_2_bagasse', '15_3_charcoal', '15_4_black_liquor', '15_5_other_biomass', 
            '16_1_biogas', '16_3_municipal_solid_waste_renewable', '16_5_biogasoline', '16_6_biodiesel',
            '16_8_other_liquid_biofuels']
elec_ou = ['17_electricity']
heat_ou = ['18_heat']
waste_ou = ['16_2_industrial_waste', '16_4_municipal_solid_waste_nonrenewable']

own_use_fuels = ['Coal', 'Oil', 'Gas', 'Renewables', 'Electricity', 'Heat', 'Waste', 'Total']

# Note, 12_1_of_which_photovoltaics is a subset of 12_solar so including will lead to double counting

use_agg_fuels_1 = ['Coal', 'Lignite', 'Oil', 'Gas', 'Nuclear', 'Hydro', 'Solar', 'Wind', 
                   'Biomass', 'Geothermal', 'Other renewables', 'Other', 'Total']
use_agg_fuels_2 = ['Coal', 'Oil', 'Gas', 'Nuclear', 'Renewables', 'Other']

heat_agg_fuels = ['Coal', 'Lignite', 'Oil', 'Gas', 'Biomass', 'Waste', 'Total']

# TECHNOLOGY aggregations for ProductionByTechnology

coal_tech = ['POW_Black_Coal_PP', 'POW_Other_Coal_PP', 'POW_Sub_BituCoal_PP', 'POW_Sub_Brown_PP', 'POW_Ultra_BituCoal_PP', 'POW_CHP_COAL_PP', 'POW_Ultra_CHP_PP']
coal_ccs_tech = ['POW_COAL_CCS_PP']
oil_tech = ['POW_Diesel_PP', 'POW_FuelOil_PP', 'POW_OilProducts_PP', 'POW_PetCoke_PP']
gas_tech = ['POW_CCGT_PP', 'POW_OCGT_PP', 'POW_CHP_GAS_PP']
gas_ccs_tech = ['POW_CCGT_CCS_PP']
nuclear_tech = ['POW_Nuclear_PP', 'POW_IMP_Nuclear_PP']
hydro_tech = ['POW_Hydro_PP', 'POW_Pumped_Hydro', 'POW_Storage_Hydro_PP', 'POW_IMP_Hydro_PP']
solar_tech = ['POW_SolarCSP_PP', 'POW_SolarFloatPV_PP', 'POW_SolarPV_PP', 'POW_SolarRoofPV_PP']
wind_tech = ['POW_WindOff_PP', 'POW_Wind_PP']
bio_tech = ['POW_Solid_Biomass_PP', 'POW_CHP_BIO_PP', 'POW_Biogas_PP']
geo_tech = ['POW_Geothermal_PP']
storage_tech = ['POW_AggregatedEnergy_Storage_VPP', 'POW_EmbeddedBattery_Storage']
waste_tech = ['POW_WasteToEnergy_PP']
other_tech = ['POW_IPP_PP', 'POW_TIDAL_PP', 'POW_CHP_PP']
# chp_tech = ['POW_CHP_PP']
im_tech = ['POW_IMPORTS_PP', 'POW_IMPORT_ELEC_PP']

lignite_tech = ['POW_Sub_Brown_PP']
thermal_coal_tech = ['POW_Black_Coal_PP', 'POW_Other_Coal_PP', 'POW_Sub_BituCoal_PP', 'POW_Ultra_BituCoal_PP', 'POW_CHP_COAL_PP', 'POW_Ultra_CHP_PP']
solar_roof_tech = ['POW_SolarRoofPV_PP']
solar_nr_tech = ['POW_SolarCSP_PP', 'POW_SolarFloatPV_PP', 'POW_SolarPV_PP']

# Another aggregation of other from Alex
other_higheragg_tech = ['POW_Solid_Biomass_PP', 'POW_CHP_BIO_PP', 'POW_Biogas_PP', 'POW_Geothermal_PP', 
                        'POW_AggregatedEnergy_Storage_VPP', 'POW_EmbeddedBattery_Storage', 'POW_WasteToEnergy_PP',
                        'POW_IPP_PP', 'POW_TIDAL_PP', 'POW_CHP_PP']

# Modern renewables

modren_elec_heat = ['POW_Hydro_PP', 'POW_Storage_Hydro_PP', 'POW_IMP_Hydro_PP', 'POW_SolarCSP_PP', 
                    'POW_SolarFloatPV_PP', 'POW_SolarPV_PP', 'POW_SolarRoofPV_PP', 'POW_WindOff_PP', 'POW_Wind_PP',
                    'POW_Solid_Biomass_PP', 'POW_CHP_BIO_PP', 'POW_Biogas_PP', 'POW_Geothermal_PP', 'POW_TIDAL_PP', 
                    'POW_CHP_BIO_PP', 'POW_Solid_Biomass_PP']

all_elec_heat = ['POW_Black_Coal_PP', 'POW_Other_Coal_PP', 'POW_Sub_BituCoal_PP', 'POW_Sub_Brown_PP', 'POW_Ultra_BituCoal_PP', 
                 'POW_CHP_COAL_PP', 'POW_Ultra_CHP_PP', 'POW_COAL_CCS_PP', 'POW_Diesel_PP', 'POW_FuelOil_PP', 'POW_FuelOil_HP', 'POW_OilProducts_PP', 'POW_PetCoke_PP',
                 'POW_CCGT_PP', 'POW_OCGT_PP', 'POW_CHP_GAS_PP', 'POW_CCGT_CCS_PP', 'POW_Nuclear_PP', 'POW_IMP_Nuclear_PP',
                 'POW_Hydro_PP', 'POW_Pumped_Hydro', 'POW_Storage_Hydro_PP', 'POW_IMP_Hydro_PP', 'POW_SolarCSP_PP', 
                 'POW_SolarFloatPV_PP', 'POW_SolarPV_PP', 'POW_SolarRoofPV_PP', 'POW_WindOff_PP', 'POW_Wind_PP', 'POW_Solid_Biomass_PP', 
                 'POW_CHP_BIO_PP', 'POW_Biogas_PP', 'POW_Geothermal_PP', 'POW_AggregatedEnergy_Storage_VPP', 'POW_EmbeddedBattery_Storage',
                 'POW_IPP_PP', 'POW_TIDAL_PP', 'POW_WasteToEnergy_PP', 'POW_WasteToHeat_HP', 'POW_CHP_PP', 'POW_HEAT_HP', 'YYY_18_heat']

# 'POW_Pumped_Hydro'?? in the above

# POW_EXPORT_ELEC_PP need to work this in

prod_agg_tech = ['Coal', 'Coal CCS', 'Oil', 'Gas', 'Gas CCS', 'Hydro', 'Nuclear', 'Wind', 'Solar', 'Bio', 
                 'Geothermal', 'Waste', 'Storage', 'Other', 'Imports', 'Total']
prod_agg_tech2 = ['Coal', 'Coal CCS', 'Lignite', 'Oil', 'Gas', 'Gas CCS', 'Hydro', 'Nuclear', 'Wind', 'Solar', 
                 'Bio', 'Geothermal', 'Waste', 'Storage', 'Other', 'Imports', 'Total']
prod_agg_tech3 = ['Coal', 'Coal CCS', 'Gas', 'Gas CCS', 'Oil', 'Nuclear', 'Hydro', 'Wind', 'Solar', 'Other', 'Imports', 'Total']

heat_prod_tech = ['Coal', 'Lignite', 'Oil', 'Gas', 'Gas CCS', 'Nuclear', 'Biomass', 'Waste', 'Non-specified', 'Other', 'Total']

# Power input fuel categories

powinput_fuel = ['Coal', 'Lignite', 'Oil', 'Gas', 'Hydro', 'Nuclear', 'Wind', 'Solar', 'Biomass', 'Geothermal',
                 'Other renewables', 'Other']

# Refinery vectors

refinery_input = ['d_ref_6_1_crude_oil', 'd_ref_6_x_ngls']
refinery_output = ['d_ref_7_1_motor_gasoline_refine', 'd_ref_7_2_aviation_gasoline_refine', 'd_ref_7_3_naphtha_refine', 
                   'd_ref_7_x_jet_fuel_refine', 'd_ref_7_6_kerosene_refine', 'd_ref_7_7_gas_diesel_oil_refine', 
                   'd_ref_7_8_fuel_oil_refine', 'd_ref_7_9_lpg_refine', 'd_ref_7_10_refinery_gas_not_liquefied_refine', 
                   'd_ref_7_11_ethane_refine', 'd_ref_7_x_other_petroleum_products_refine']

refinery_new_output = ['7_1_from_ref', '7_2_from_ref', '7_3_from_ref', '7_jet_from_ref', '7_6_from_ref', '7_7_from_ref',
                       '7_8_from_ref', '7_9_from_ref', '7_10_from_ref', '7_11_from_ref', '7_other_from_ref']

# Capacity vectors
    
coal_cap = ['POW_Black_Coal_PP', 'POW_Sub_BituCoal_PP', 'POW_Sub_Brown_PP', 'POW_CHP_COAL_PP', 'POW_Other_Coal_PP', 'POW_Ultra_BituCoal_PP', 'POW_Ultra_CHP_PP']
coal_ccs_cap = ['POW_COAL_CCS_PP']
gas_cap = ['POW_CCGT_PP', 'POW_OCGT_PP', 'POW_CHP_GAS_PP']
gas_ccs_cap = ['POW_CCGT_CCS_PP']
oil_cap = ['POW_Diesel_PP', 'POW_FuelOil_PP', 'POW_OilProducts_PP', 'POW_PetCoke_PP']
nuclear_cap = ['POW_Nuclear_PP', 'POW_IMP_Nuclear_PP']
hydro_cap = ['POW_Hydro_PP', 'POW_Pumped_Hydro', 'POW_Storage_Hydro_PP', 'POW_IMP_Hydro_PP']
bio_cap = ['POW_Solid_Biomass_PP', 'POW_CHP_BIO_PP', 'POW_Biogas_PP']
wind_cap = ['POW_Wind_PP', 'POW_WindOff_PP']
solar_cap = ['POW_SolarCSP_PP', 'POW_SolarFloatPV_PP', 'POW_SolarPV_PP', 'POW_SolarRoofPV_PP']
geo_cap = ['POW_Geothermal_PP']
storage_cap = ['POW_AggregatedEnergy_Storage_VPP', 'POW_EmbeddedBattery_Storage']
waste_cap = ['POW_WasteToEnergy_PP']
other_cap = ['POW_IPP_PP', 'POW_TIDAL_PP', 'POW_CHP_PP']
# chp_cap = ['POW_CHP_PP']
# 'POW_HEAT_HP' not in electricity capacity
transmission_cap = ['POW_Transmission']

lignite_cap = ['POW_Sub_Brown_PP']
thermal_coal_cap = ['POW_Black_Coal_PP', 'POW_Other_Coal_PP', 'POW_Sub_BituCoal_PP', 'POW_Ultra_BituCoal_PP', 'POW_CHP_COAL_PP', 'POW_Ultra_CHP_PP']

# Other cap from Alex
other_higheragg_cap = ['POW_Solid_Biomass_PP', 'POW_CHP_BIO_PP', 'POW_Biogas_PP', 'POW_Geothermal_PP', 'POW_AggregatedEnergy_Storage_VPP', 
                       'POW_EmbeddedBattery_Storage', 'POW_WasteToEnergy_PP', 'POW_IPP_PP', 'POW_TIDAL_PP', 'POW_CHP_PP']

pow_capacity_agg = ['Coal', 'Coal CCS', 'Gas', 'Gas CCS', 'Oil', 'Nuclear', 'Hydro', 'Bio', 'Wind', 'Solar', 'Geothermal', 'Waste', 'Storage', 'Other']
pow_capacity_agg2 = ['Coal', 'Coal CCS', 'Lignite', 'Gas', 'Gas CCS', 'Oil', 'Nuclear', 'Hydro', 'Bio', 'Wind', 
                     'Solar', 'Geothermal', 'Waste', 'Storage', 'Other']

pow_capacity_agg3 = ['Coal', 'Coal CCS', 'Gas', 'Gas CCS', 'Oil', 'Nuclear', 'Hydro', 'Wind', 'Solar', 'Other', 'Total']

# Heat power plants

coal_heat = ['POW_CHP_COAL_PP', 'POW_Ultra_BituCoal_PP', 'POW_Ultra_CHP_PP', 'POW_HEAT_COKE_HP', 'POW_Sub_BituCoal_PP', 'POW_Other_Coal_PP']
lignite_heat = ['POW_Sub_Brown_PP']
gas_heat = ['POW_CCGT_PP', 'POW_CHP_GAS_PP']
gas_ccs_heat = ['POW_CCGT_CCS_PP']
oil_heat = ['POW_FuelOil_HP', 'POW_Diesel_PP', 'POW_FuelOil_PP', 'POW_OilProducts_PP']
bio_heat = ['POW_CHP_BIO_PP', 'POW_Solid_Biomass_PP', 'POW_Biogas_PP']
nuke_heat = ['POW_Nuclear_PP']
waste_heat = ['POW_WasteToEnergy_PP', 'POW_WasteToHeat_HP']
combination_heat = ['POW_HEAT_HP', 'YYY_18_heat']
nons_heat = ['POW_CHP_PP']

# Heat only power plants

heat_only = ['POW_FuelOil_HP', 'POW_HEAT_HP', 'POW_WasteToHeat_HP', 'POW_HEAT_COKE_HP', 'YYY_18_heat']

# Make space for charts (before data/tables)
chart_height = 18 # number of excel rows before the data is written (can change this)

# Define column chart years
col_chart_years = ['2000', '2010', '2018', '2020', '2030', '2040', '2050']

# Define column chart years for transport
col_chart_years_transport = ['2018', '2020', '2030', '2040', '2050']

# Transformation chart years
trans_col_chart = ['2018', '2020', '2030', '2040', '2050']
gen_col_chart_years = ['2000', '2010', '2018', '2020', '2030', '2040', '2050']

# FED aggregate fuels

FED_agg_fuels = ['Coal', 'Oil', 'Gas', 'Other renewables', 'Biomass', 'Hydrogen', 'Electricity', 'Heat', 'Others']
FED_agg_fuels_ind = ['Coal', 'Oil', 'Gas', 'Biomass', 'Hydrogen', 'Electricity', 'Heat', 'Others']
Transport_fuels_agg = ['Diesel', 'Gasoline', 'LPG', 'Gas', 'Jet fuel', 'Electricity', 'Renewables', 'Hydrogen', 'Other']

# FED aggregate sectors

FED_agg_sectors = ['Industry', 'Transport', 'Buildings', 'Agriculture', 'Non-energy', 'Non-specified']
Industry_eight = ['Iron & steel', 'Chemicals', 'Aluminium', 'Non-metallic minerals', 'Mining', 'Pulp & paper', 'Other', 'Non-specified']
Transport_modal_agg = ['Aviation', 'Road', 'Rail' ,'Marine', 'Pipeline', 'Non-specified']

# TPES

TPES_agg_fuels1 = ['Coal', 'Oil', 'Gas', 'Nuclear', 'Renewables', 'Electricity', 'Hydrogen', 'Other fuels']
TPES_agg_fuels2 = ['Coal', 'Oil', 'Gas', 'Nuclear', 'Renewables', 'Other fuels']
TPES_agg_trade = ['Coal', 'Crude oil & NGL', 'Refined products', 'Gas', 
                  'Renewables', 'Electricity', 'Hydrogen', 'Other fuels']
avi_bunker = ['Aviation gasoline', 'Jet fuel', 'Biojet kerosene', 'Hydrogen']

nettrade_order = ['Coal', 'Crude oil & NGL', 'Refined products', 'Gas', 'Renewables', 'Electricity', 'Hydrogen', 'Trade balance']
