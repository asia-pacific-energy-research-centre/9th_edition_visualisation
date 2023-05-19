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
#%%
##############################################################################

#import mappings:
sector_plotting_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='sectors_plotting')
# sector_plotting_mappings.columns Index(['sectors_plotting', 'sectors', 'sub1sectors', 'sub2sectors'], dtype='object')

fuel_plotting_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='fuels_plotting')
# fuel_plotting_mappings.columns Index(['fuels_plotting', 'fuels', 'subfuels'], dtype='object')

transformation_sector_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='transformation_sector_mappings')
# transformation_sector_mappings.columns: input_fuel	transformation_sectors	sub1sectors

economy_mappings = pd.read_csv('../config/economy_code_to_name.csv')
# economy_mappings.columns: Index(['economy', 'economy_name', 'alt_aperc_code', 'alt_aperc_code2','region1', 'region2_test', 'region3_aperc_code'],dtype='object')

#%%
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
    
#%%
#######################
#attempting to change the values in the columns and some column names
#first manually change some of the column names to make them easier to work with. this will help prevent mixing up fuel values with sector values etc
column_changes_dict = {}
column_changes_dict['FUEL'] = 'fuels_8th'
column_changes_dict['Fuel'] = 'fuels_8th'
column_changes_dict['fuel_code'] = 'fuels_8th'
column_changes_dict['item_code_new'] = 'sectors_8th'
column_changes_dict['Transformation'] = 'sectors_8th'
column_changes_dict['Generation'] = 'sectors_8th'
column_changes_dict['Sector'] = 'sectors_8th'
column_changes_dict['TECHNOLOGY'] = 'sectors_8th'
column_changes_dict['Technology'] = 'sectors_8th'

#now change the columns
table_tuple_columns_mapped = ()
excludeable_cols = ['sheet', 'unit', 'table_number','Economy']
for table_group in table_tuple:

    #there is one example where we cannot use column_changes_dict because the column name TECHNOLOGY refers to fuel and Generation is the sector. So if both these columns exist we will change the TECHNOLOGY column to fuels
    if 'TECHNOLOGY' in table_group.columns and 'Generation' in table_group.columns:
        table_group = table_group.rename(columns={'TECHNOLOGY':'fuels_8th'})
        table_group = table_group.rename(columns={'Generation':'sectors_8th'})
    else:
        #change cols according to column_changes_dict
        table_group = table_group.rename(columns=column_changes_dict)
    #and create a new column called 'COLUMN_plotting' for each column except the excludeable_cols, but make it empty
    # for col in table_group.columns:
    #     if col in excludeable_cols:
    #         continue
    #     table_group[col + '_plotting'] = np.nan
    #now add the table_group to the tuple
    table_tuple_columns_mapped = table_tuple_columns_mapped + (table_group,)

#now using this we will loop through the table and try to map the values in sectors_8th and fuels_8th to the sectors_plotting and fuels_plotting columns in sector_plotting_mappings and fuel_plotting_mappings. i.e. where the value in sectors_8th is equal to a value in sector_plotting_mappings['sectors_plotting'] then fill sectors_plotting with that value. Same for fuels_8th and fuels_plotting_mappings
sector_plotting_mappings_new = sector_plotting_mappings.copy()
sector_plotting_mappings_new['sectors_8th'] = sector_plotting_mappings_new['sectors_plotting']
sector_plotting_mappings_new = sector_plotting_mappings_new[['sectors_plotting', 'sectors_8th']]
fuel_plotting_mappings_new = fuel_plotting_mappings.copy()
fuel_plotting_mappings_new['fuels_8th'] = fuel_plotting_mappings_new['fuels_plotting']
fuel_plotting_mappings_new = fuel_plotting_mappings_new[['fuels_plotting', 'fuels_8th']]
#%%
#note that we wil only be mapping values if they are in a fuels_8th or sectors_8th column. we will not be mapping values in other columns. 
table_tuple_values_mapped = ()
for i, table_group in enumerate(table_tuple_columns_mapped):
    # if i == 1:
    #     break
    # if the table_group has a column called sectors_8th then map the values in that column to the sectors_plotting column
    #if the table_group has a column called fuels_8th then map the values in that column to the fuels_plotting column
    if 'sectors_8th' in table_group.columns:
        table_group = table_group.merge(sector_plotting_mappings_new, how='left', on='sectors_8th')
        #rename sectors_plotting to sectors_8th_plotting
        table_group = table_group.rename(columns={'sectors_plotting':'sectors_8th_plotting'})
    if 'fuels_8th' in table_group.columns:
        table_group = table_group.merge(fuel_plotting_mappings_new, how='left', on='fuels_8th')
        #rename fuels_plotting to fuels_8th_plotting
        table_group = table_group.rename(columns={'fuels_plotting':'fuels_8th_plotting'})
    #now add the table_group to the tuple
    table_tuple_values_mapped = table_tuple_values_mapped + (table_group,)

#now we have a tuple of tables with a lot of the values mapped. We can now use this to create the config file more easily as we already know what the actual values are for a lot of the columns.


#%%
#we will also use the two sheets: 8th_name_to_plotting_name, 8th_name_to_plot_name_specific to map missing values to plotting names (because they are not names we want in our plotting_sectors or plotting_fuels mappings). THey are iun visualisation_config.xlsx

#first we will create a dictionary of the values in the 8th_name_to_plotting_name sheet
#and then the specific names one, we ahve to search for sheets which match the sheet column first.

#Do specific ones first: and for the specific names we will do a filter for the sheet name and then do the same
name_to_plot_name_specific = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='8th_name_to_plot_name_specific')
table_tuple_values_mapped3 = ()
for i, table_group in enumerate(table_tuple_values_mapped):
    for col in table_group.columns:
        if col in excludeable_cols or '_plotting' in col:
            continue
        for i, row in name_to_plot_name_specific.iterrows():
            col_to_change = row['column']
            if col_to_change != col:
                continue#bit inefficient but watevs
            sheet = row['sheet']
            old_name = row['8th_name']
            new_name = row['plotting_name']
            #where sheet name = sheet and the value in the col is equal to old_name, change the col+_plotting to new_name
            table_group.loc[(table_group['sheet'] == sheet) & (table_group[col] == old_name), col + '_plotting'] = new_name
    #now add the table_group to the tuple
    table_tuple_values_mapped3 = table_tuple_values_mapped3 + (table_group,)
#%%
##########
name_to_plotting_name = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='8th_name_to_plotting_name')

#now make changes
table_tuple_values_mapped2 = ()
for i, table_group in enumerate(table_tuple_values_mapped3):
    # if i == 1:
    #     break
    for col in table_group.columns:
        if col in excludeable_cols or '_plotting' in col:
            continue
        for i, row in name_to_plotting_name.iterrows():
            col_to_change = row['column']
            if col_to_change != col:
                continue
            old_name = row['8th_name']
            new_name = row['plotting_name']
            #where the value in the col is equal to old_name, change the col+_plotting to new_name
            table_group.loc[table_group[col] == old_name, col + '_plotting'] = new_name
            
    #now add the table_group to the tuple
    table_tuple_values_mapped2 = table_tuple_values_mapped2 + (table_group,)



#%%
#we will save the data again in a new file:
#save the data
with pd.ExcelWriter('../intermediate_data/config/charts_mapping_9th_computer_generated.xlsx') as writer:
    for i, table_group in enumerate(table_tuple_values_mapped2):
        table_group.to_excel(writer, sheet_name=str(i), index=False)


#%%

#next step will include creating new datasets which create aggregations of data to match some of the categories plotted in the 8th edition. 
#for example we need an aggregation of the transformation sector input and output values to create entries for Power, Refining or Hydrogen

#first we import the transformation mappigns from the visualisation_category_mappings.xlsx file
transformation_sector_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='transformation_sector_mappings')
#Index(['input_fuel', 'sectors_plotting', 'sectors','sub1sectors'], dtype='object')

#the input_fuel col is a bool and determines whether we are looking for input or output fuels from the transformation sector. If input then the values will be negative, if output then positive

#we will create a new dataframe which is the aggregation of the sectors in the transformation_sector_mappings dataframe, applied to the 9th modelling data. 
#we will create a column within this dataframe called sectors_plotting which will then be able to be stacked with the other columns in other dataframes with the same column name

model_df_wide_transformation = model_df_wide.copy()
#make the data long so we can filter for negative and positive values
#fgirst grab object copls as the index cols
index_cols = model_df_wide_transformation.select_dtypes(include=['object']).columns
#now melt the data
model_df_transformation = pd.melt(model_df_wide_transformation, id_vars=index_cols, var_name='year', value_name='value')

#join the transformation_sector_mappings dataframe to the model_df_wide_transformation dataframe
model_df_transformation = model_df_transformation.merge(transformation_sector_mappings, how='right', on=['sectors','sub1sectors'])
#now separaten into input and output dfs using book and whtehr value is positive or negative
input_transformation = model_df_transformation[(model_df_transformation['input_fuel'] == True) & (model_df_transformation['value'] < 0)]

output_transformation = model_df_transformation[(model_df_transformation['input_fuel'] == False) & (model_df_transformation['value'] > 0)]

#Thats it. We will stack this with the other dataframes later on. We wont sum up by plotting_sector yet as we will do that later on when we have all the dataframes stacked together (the extra info is usefuul right now)


#%%
#now we will join the plotting sectors and plotting fuels mappings to the model_df_wide dataframe to extract the data we need for those sectors and fuels
# sector_plotting_mappings
# fuel_plotting_mappings

#join model_df_wide to sector_plotting_mappings suing left join. HOwever it is a bit complicated because we will need to do a 
model_df_wide_sectors = model_df_wide.merge(sector_plotting_mappings, how='left', on=['sectors','sub1sectors','sub2sectors'])

