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

#make model_df_wide into model_df_tall
#fgirst grab object copls as the index cols
index_cols = model_df_wide.select_dtypes(include=['object']).columns
#now melt the data
model_df_wide = pd.melt(model_df_wide, id_vars=index_cols, var_name='year', value_name='value')
#todo

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
#these will be mappings from the names used to refer to categories shown in the plotting, to the combinations of column categories from which these categories are aggregated from.
# Eg: Buildings is extracted by finding all values with 16_01_buildings in their sub1sectors column. Also Bunkers is extacted by finding all values with 04_international_marine_bunkers or 05_international_aviation_bunkers in their sectors column

sector_plotting_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='sectors_plotting')
# sector_plotting_mappings.columns Index(['sectors_plotting', 'sectors', 'sub1sectors', 'sub2sectors'], dtype='object')

fuel_plotting_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='fuels_plotting')
# fuel_plotting_mappings.columns Index(['fuels_plotting', 'fuels', 'subfuels'], dtype='object')

transformation_sector_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='transformation_sector_mappings')
# transformation_sector_mappings.columns: input_fuel	transformation_sectors	sub1sectors

economy_mappings = pd.read_csv('../config/economy_code_to_name.csv')
# economy_mappings.columns: Index(['economy', 'economy_name', 'alt_aperc_code', 'alt_aperc_code2','region1', 'region2_test', 'region3_aperc_code'],dtype='object')
#%%
#############################
#for fuel and sector mappings we will extract the most sepcific reference for each row and then record it's column in a column called 'column'.
#so for example, where we want to extract the reference for the sectors_plotting value Agriculture, we find the rightmost column that is not na (this is the msot specific column), set 'reference_sector' to that value in the most specific column, and then the column to the name of the most specific column
new_sector_plotting_mappings = pd.DataFrame(columns=['sectors_plotting', 'reference_sector', 'reference_column'])

ordered_columns = [ 'sub2sectors', 'sub1sectors','sectors']
for col in ordered_columns:
    #extract rows where the value is not na in this col

    #loop through the rows

        #create new row in new_sector_plotting_mappings
        #set sectors_plotting to sectors_plotting
        #reference_sector to col value
        #reference_column to col

    #remove these rows from the sector_plotting_mappings


#do the same for fuels

#now check for nas in the entire dfs

#save in intermediate data
plotting_sector_mappings.to_csv(f'../intermediate_data/config/plotting_sector_mappings_{FILE_DATE_ID}.csv', index=False)
plotting_fuel_mappings.to_csv(f'../intermediate_data/config/plotting_fuel_mappings_{FILE_DATE_ID}.csv', index=False)
transformation_sector_mappings.to_csv(f'../intermediate_data/config/transformation_sector_mappings_{FILE_DATE_ID}.csv', index=False)

#############################
#and now these mappings can be joined to the model_df and used to extract the data needed for each plotting_name
#note that (i think) it works if you :
# copy model df tall. called it sector_model_df_tall
# in sector_model_df_tall join the sector plotting names (left join).  #note this will need to be done a special way because its no simple join
# remove the sector columns. 
# copy model df tall again, called it sector_blank
# in sector_blank, remove the sector columns and create new sector_plotting column and fill it with np.nan #this allows for when the graph might not need a sectort. but tbh would expect it to need at least sector = total?
# stack sector_blank on sector_model_df_tall
# join fuels_plotting to sector_model_df_tall using left join?   #note this will need to be done a special way because its no simple join
#drop the other fuels columns

#what about if we need sectors where fuels are blank? i dont think its liekly though? because without a definition for sector you will get double ups, for example form the sum of TFEC and TFC.

#now we have a df with only the columns fuels_plotting and sectors_plotting which contains defintiions of all the possible combinations of fuels_plotting and sectors_plotting we could have.. i think.
#call it plotting_df


#%%
#############################
#now we can extract the data for each graph we need to produce using the file D:\APERC\9th_edition_visualisation\intermediate_data\config\charts_mapping_9th_computer_generated.xlsx
#
#for now jsut use the sheet called 1
#for each unique sheet, table_numbers combination, extract the values form the cols sectors_8th_plotting and fuels_8th_plotting which specifies the data we need to grab from the new plotting_df
#merge these cols with the plotting_df and grab the values.

#############################
#next step will include creating new datasets which create aggregations of data to match some of the categories plotted in the 8th edition. 
#for example we need an aggregation of the transformation sector input and output values to create entries for Power, Refining or Hydrogen

#first we import the transformation mappigns from the visualisation_category_mappings.xlsx file
transformation_sector_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='transformation_sector_mappings')
#Index(['input_fuel', 'sectors_plotting', 'sectors','sub1sectors'], dtype='object')

#the input_fuel col is a bool and determines whether we are looking for input or output fuels from the transformation sector. If input then the values will be negative, if output then positive

#we will create a new dataframe which is the aggregation of the sectors in the transformation_sector_mappings dataframe, applied to the 9th modelling data. 
#we will create a column within this dataframe called sectors_plotting which will then be able to be stacked with the other columns in other dataframes with the same column name

model_df_tall_transformation = model_df_tall.copy()
#join the transformation_sector_mappings dataframe to the model_df_tall_transformation dataframe
model_df_transformation = model_df_transformation.merge(transformation_sector_mappings, how='right', on=['sectors','sub1sectors'])

#and join the fuel_plotting mapping to the df #note this will need to be done a special way because its no simple join
model_df_transformation = model_df_transformation.merge(fuels_plotting, how='right', on=['sectors','sub1sectors'])
 
#now separaten into input and output dfs using book and whtehr value is positive or negative
input_transformation = model_df_transfo rmation[(model_df_transformation['input_fuel'] == True) & (model_df_transformation['value'] < 0)]

output_transformation = model_df_transformation[(model_df_transformation['input_fuel'] == False) & (model_df_transformation['value'] > 0)]

#Thats it. We will stack this with the other dataframes later on. We wont sum up by plotting_sector yet as we will do that later on when we have all the dataframes stacked together (the extra info is usefuul right now)

#%%
#now we will join the plotting sectors and plotting fuels mappings to the model_df_tall dataframe to extract the data we need for those sectors and fuels
# sector_plotting_mappings
# fuel_plotting_mappings

#join model_df_tall to sector_plotting_mappings suing left join. HOwever it is a bit complicated because we will need to do a  #note this will need to be done a special way because its no simple join
model_df_tall_sectors = model_df_tall.merge(sector_plotting_mappings, how='left', on=['sectors','sub1sectors','sub2sectors'])

#now stack with the transformation data we did earlier
plotting_df = pd.concat([])

#sum up the values by the ?object cols? so we dont accidentally sum up by economy or somethign else. 
plotting_df = #

#since we havent gotten to specifiying the atual plot that is required, just plot a line graph with matplotlib. save it with the name being the same as the unique sheet, table_numbers combination and save it in output\plotting_output

#%%
#############################
 