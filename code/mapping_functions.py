#Functions used in 1_map_9th_data_to_plotting_template.py. They are to do with mapping but include some adjacent tasks such as data checking, plotting and formatting.
import pickle
import pandas as pd
import numpy as np

import collections
STRICT_DATA_CHECKING = False
        
def format_plotting_mappings(sector_plotting_mappings, fuel_plotting_mappings):
    #will loop through the sector_plotting_mappings and fuel_plotting_mappings and create a new df where only the most specific sector/fuel columns is referenced as teh reference_column (which is the column from which to look for the refererence_sector/fuel when extracting the data for the plotting_sector/fuel). Each plotting_sector/fuel might have multiple reference_sector/fuels from any number of different reference columns.
    new_sector_plotting_mappings = pd.DataFrame(columns=['sectors_plotting', 'reference_sector', 'reference_column'])
    ordered_columns = [ 'sub2sectors', 'sub1sectors','sectors']
    for col in ordered_columns:
        #extract rows where the value is not na in this col
        for row in sector_plotting_mappings[sector_plotting_mappings[col].notna()].index:
            #loop through the rows
            row_x = sector_plotting_mappings.loc[row]
            #create new row in new_sector_plotting_mappings
            new_row = pd.DataFrame({'sectors_plotting': [row_x['sectors_plotting']],
                        'reference_sector': [row_x[col]],
                        'reference_column': [col]})

            new_sector_plotting_mappings = pd.concat([new_sector_plotting_mappings, new_row], ignore_index=True)

        #remove these rows from the sector_plotting_mappings so that we don't double count them
        sector_plotting_mappings = sector_plotting_mappings[sector_plotting_mappings[col].isna()]

    #do the same for fuels
    new_fuel_plotting_mappings = pd.DataFrame(columns=['fuels_plotting', 'reference_fuel', 'reference_column']) 

    ordered_columns = [ 'subfuels', 'fuels']
    for col in ordered_columns:
        #extract rows where the value is not na in this col
        for row in fuel_plotting_mappings[fuel_plotting_mappings[col].notna()].index:
            #loop through the rows
            row_x = fuel_plotting_mappings.loc[row]
            #create new row in new_sector_plotting_mappings
            new_row = pd.DataFrame({'fuels_plotting': [row_x['fuels_plotting']],
                        'reference_fuel': [row_x[col]],
                        'reference_column': [col]})

            new_fuel_plotting_mappings = pd.concat([new_fuel_plotting_mappings, new_row], ignore_index=True)

        #remove these rows from the sector_plotting_mappings so that we don't double count them
        fuel_plotting_mappings = fuel_plotting_mappings[fuel_plotting_mappings[col].isna()]

    #now check for nas in the entire dfs
    if new_sector_plotting_mappings.isna().sum().sum() > 0:
        if STRICT_DATA_CHECKING:
            raise('There are still some nas in the new_sector_plotting_mappings')
    if new_fuel_plotting_mappings.isna().sum().sum() > 0:
        if STRICT_DATA_CHECKING:
            raise('There are still some nas in the new_fuel_plotting_mappings')
        
    return new_sector_plotting_mappings, new_fuel_plotting_mappings

def check_charts_mapping_group_2_cols(charts_mapping):
    #filter for where sectors_plotting and fuels_plotting are both na. if there are any rows, throw an error
    charts_mapping_nas = charts_mapping[charts_mapping['sectors_plotting'].isna() & charts_mapping['fuels_plotting'].isna()]
    if len(charts_mapping_nas) > 0:
        print(charts_mapping_nas)
        raise Exception('There are rows in charts_mapping where both sectors_plotting and fuels_plotting are na. This is not allowed. Please fix this in the charts_mapping sheet in master_config.xlsx')
    
    #then filter for where they are both not na. if there are any rows, throw an error
    charts_mapping_nas = charts_mapping[charts_mapping['sectors_plotting'].notna() & charts_mapping['fuels_plotting'].notna()]
    if len(charts_mapping_nas) > 0:
        print(charts_mapping_nas)
        raise Exception('There are rows in charts_mapping where both sectors_plotting and fuels_plotting are not na. This is not allowed. Please fix this in the charts_mapping sheet in master_config.xlsx')
    
def format_charts_mapping(charts_mapping):
    #this df has a unique format that isnt easy to work with. Firstly, the top row is a header to make it easy to fill in manually, so drop it. Then on the next rwo are three gorups of cols essentially, each with a different purpose.
    #group 1: sheet_name	table_number	chart_type
    #group 2 (the aggregate): fuels_plotting	sectors_plotting
    #group 3 (plotting_names): (which are just numbers from 0 onwards)
    #leave group 1 as is.
    # for group 2, we will split the dataframe depending on if fuels plotting or sectors plotting is na. if neither or both , throw and error. if one or the other, then we will have a df 'fuels_plotting' which is where fuels_plotting is na (hterefore sectors plotting is the aggregate), and sectors_plotting which is where sectors_plotting is na (therefore fuels plotting is the aggregate)
    #then for both of these we will deal with group 3 in the same way:
    #for group 3, drop the column in fuels_plotting or sectors_plotting that is na(this is the plotting name column). set 'plotting name' to the name of the col that is na (eg. plotting_name  = 'fuels_plotting' if the column fuels plotting is na and sectors plotting is the aggregate). then melt the dataframe so that the group 3 columns (plotting name cols) are all in one col. drop the col names (the digits) and drop nas from the new col
    #then concat the two dfs together!
    
    #every column after: [sheet	table_number	chart_type ] will be melted into a plotting_name column. then remove nas from plotting_name column
    #but to be safe, double check that these columns are just digits, becuase if there are new cols added, this will break
    key_cols = ['sheet_name', 'table_number', 'chart_type']
    group_2_cols = ['fuels_plotting', 'sectors_plotting']
    group_3_cols = [x for x in charts_mapping.columns.tolist() if x not in key_cols + group_2_cols]
    if not all([str(x).isdigit() for x in group_3_cols]):
        raise Exception('plotting name columns are not all named with digits')
            
    # for group 2, we will split the dataframe depending on if fuels plotting or sectors plotting is na. if both, then we will have a df 'fuels_plotting' which is where fuels_plotting is not na,, and sectors_plotting which is where sectors_plotting is not na.
    check_charts_mapping_group_2_cols(charts_mapping)
    temp_dict = {} 
    temp_dict['charts_mapping_sectors_plotting'] = charts_mapping.dropna(subset=['sectors_plotting'])
    temp_dict['charts_mapping_fuels_plotting'] = charts_mapping.dropna(subset=['fuels_plotting'])
    
    #for group 3, drop the column in fuels_plotting or sectors_plotting that is na. set 'plotting name' to the name of the col that is not na (eg. plotting_name  = 'fuels_plotting' if the column fuels plotting is not na). then melt the dataframe so that the group 3 columns are all in one col, with the name of the col with na's. drop the col names (the digits) and drop nas from the new col
    #then concat the two dfs together!
    
    ######################################################
    #where sectors_plotting is na (therefore the plotting names will be sectors):
    aggregated_by_sector = charts_mapping.dropna(subset=['sectors_plotting'])
    plotting_column = 'fuels_plotting'
    aggregate_column = 'sectors_plotting'
    aggregated_by_sector.drop(columns=[plotting_column], inplace=True)
    aggregated_by_sector = pd.melt(aggregated_by_sector, id_vars=key_cols + [aggregate_column], value_name=plotting_column, var_name='digits')
    aggregated_by_sector = aggregated_by_sector.drop(columns=['digits'])
    #drop nas in plotting_column
    aggregated_by_sector = aggregated_by_sector.dropna(subset=[plotting_column])
    #set 'plotting_column' to plotting_column
    aggregated_by_sector['plotting_column'] = plotting_column
    aggregated_by_sector['aggregate_column'] = aggregate_column
    
    #where fuels_plotting is na (therefore the plotting names will be fuels):
    aggregated_by_fuels = charts_mapping.dropna(subset=['fuels_plotting'])
    plotting_column = 'sectors_plotting'
    aggregate_column = 'fuels_plotting'
    aggregated_by_fuels.drop(columns=[plotting_column], inplace=True)
    aggregated_by_fuels = pd.melt(aggregated_by_fuels, id_vars=key_cols + [aggregate_column], value_name=plotting_column, var_name='digits')
    aggregated_by_fuels = aggregated_by_fuels.drop(columns=['digits'])
    #drop nas in plotting_column
    aggregated_by_fuels = aggregated_by_fuels.dropna(subset=[plotting_column])
    #set 'plotting_column' to plotting_column
    aggregated_by_fuels['plotting_column'] = plotting_column
    aggregated_by_fuels['aggregate_column'] = aggregate_column
    #concat the two dfs together
    new_charts_mapping = pd.concat([aggregated_by_sector, aggregated_by_fuels])
    
    #concat unique sheet and table_numbers cols
    new_charts_mapping['table_id'] = new_charts_mapping['sheet_name'] + '_' + new_charts_mapping['table_number'].astype(str)

    return new_charts_mapping

# def format_charts_mapping(charts_mapping):
#     #every column after: [sheet	table_number	chart_type ] will be melted into a plotting_name column. then remove nas from plotting_name column
#     #but to be safe, double check that these columns are just digits, becuase if there are new cols added, this will break
#     key_cols = ['sheet_name', 'table_number', 'chart_type']
#     cols_after_table = [x for x in charts_mapping.columns.tolist() if x not in key_cols]
#     if not all([str(x).isdigit() for x in cols_after_table]):
#         raise Exception('columns after table are not all digits')
            
#     new_charts_mapping = charts_mapping.copy()
#     #melt the data
#     new_charts_mapping = pd.melt(new_charts_mapping, id_vars=key_cols, value_name='plotting_name', var_name='digits')
#     #drop digits
#     new_charts_mapping = new_charts_mapping.drop(columns=['digits'])
#     new_charts_mapping = new_charts_mapping.dropna(subset=['plotting_name'])

#     #concat unique sheet and table_numbers cols
#     new_charts_mapping['table_id'] = new_charts_mapping['sheet_name'] + '_' + new_charts_mapping['table_number'].astype(str)

#     return new_charts_mapping

def test_charts_mapping(charts_mapping):
    #things to test:
    #where there is a bar chart, it is the only chart for that table number, else throw error (this is because bar charts are split by 10 year intervals so need their own table.)
    bar_charts = charts_mapping[charts_mapping['chart_type'] == 'bar']
    #chekc if the table id is anywher else in the df
    non_bar_charts = charts_mapping[charts_mapping['chart_type'] != 'bar']
    errors = bar_charts[bar_charts['table_id'].isin(non_bar_charts['table_id'].unique().tolist())]
    if len(errors) > 0:
        print(errors)
        raise Exception('There is a bar chart that is not the only chart for that table id. This shouldnt happen because bar charts are split by X year intervals so need their own table.')

def save_plotting_names_order(charts_mapping,FILE_DATE_ID):
    key_cols = ['sheet_name', 'table_number', 'chart_type']
    group_2_cols = ['fuels_plotting', 'sectors_plotting']
    group_3_cols = [x for x in charts_mapping.columns.tolist() if x not in key_cols + group_2_cols]
    #create table_id col
    charts_mapping['table_id'] = charts_mapping['sheet_name'] + '_' + charts_mapping['table_number'].astype(str)

    charts_mapping_pivot = charts_mapping[['table_id'] + group_3_cols].drop_duplicates()
    #set index to 'table_id'
    charts_mapping_pivot = charts_mapping_pivot.set_index('table_id')
    # #drop nas
    # charts_mapping_pivot = charts_mapping_pivot.dropna()
    #put it into a dictionary such that every key is  the 'table_id', and the value is a list of the group_3_cols in order, excluding nas
    plotting_names_order = {}
    for table_id in charts_mapping_pivot.index.tolist():
        plotting_names_order[table_id] = [x for x in charts_mapping_pivot.loc[table_id].tolist() if str(x) != 'nan']
    
    # Save dictionary into file
    with open(f'../intermediate_data/config/plotting_names_order_{FILE_DATE_ID}.pkl', 'wb') as handle:
        pickle.dump(plotting_names_order, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
def check_data_matches_expectations(model_df_wide_economy, model_variables,RAISE_ERROR=True):
    #drop first 2 rows (includes the columns row) and check the next row is a set of columns that match the object columns in the Data sheet

    #we first need to check that the columns in the Variables sheet match the columns in the Data sheet
    object_columns = model_df_wide_economy.select_dtypes(include=['object']).columns
    #check the difference between the columns in the Variables sheet and the columns in the Data sheet
    diff = np.setdiff1d(model_variables.columns, object_columns)

    if len(diff) > 0:
        print('The following columns between the Variables sheet and the Data are different: ', diff)
        raise Exception('The columns in the Variables sheet do not match the columns in the Data sheet')

    #Now check that the unique variables in the columns in the Variables sheet match the unique variables in the columns in the Data sheet
    for col in object_columns:
        unique_variables = model_variables[col].dropna().unique()
        unique_variables.sort()
        unique_variables_data = model_df_wide_economy[col].dropna().unique()
        unique_variables_data.sort()
        diff = np.setdiff1d(unique_variables, unique_variables_data)
        data_sheet_missing_list = []
        variables_missing_list = []
        if len(diff) > 0:
            #determine whether its missing from the Variables sheet or the Data sheet
            for variable in diff:
                #skip the economy column
                if col == 'economy':
                    continue
                elif variable in unique_variables:
                    if RAISE_ERROR:
                        raise Exception('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
                    # print('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
                    data_sheet_missing_list.append(variable)
                else:
                    if RAISE_ERROR:
                        raise Exception('The variable {} in the column {} is missing from the Variables sheet'.format(variable, col))
                    # print('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
                    variables_missing_list.append(variable)
            if len(data_sheet_missing_list) > 0:
                print('In the column {}, these variables are missing from the Data sheet {}'.format(col, data_sheet_missing_list))
            if len(variables_missing_list) > 0:
                print('In the column {}, these variables are missing from the Variables sheet {}'.format(col, variables_missing_list))

def merge_sector_mappings(model_df_tall, new_sector_plotting_mappings,sector_plotting_mappings,  RAISE_ERROR=True):
    breakpoint()
    #using the plotting mappings which were created in the format_plotting_mappings function, we need to merge these onto the model_df_tall using the reference_column and reference_sector columns, where the reference column specifies the column to find the reference sector in the model_df_tall
    new_model_df_tall = model_df_tall.copy()
    #empty it
    new_model_df_tall = new_model_df_tall[0:0]
    #so join the new_sector_plotting_mappings to the model_df_tall
    for unique_col in new_sector_plotting_mappings.reference_column.unique():
        columns_data = new_sector_plotting_mappings[new_sector_plotting_mappings.reference_column == unique_col][['sectors_plotting', 'reference_sector']]
        #filter for the unique col and then join on the unique col to the model_df_tall
        columns_data = model_df_tall.merge(columns_data, how='inner', left_on=unique_col, right_on='reference_sector')#use inner so we only get the rows that match each other
        #concat to the new_model_df_tall
        new_model_df_tall = pd.concat([new_model_df_tall, columns_data])
    
    #and to be more precise, check the uniqe rows for the columns [[sectors_plotting	sectors	subsectors]] in the sectors_mappings are all in the new_new_model_df_tall    
    new_df = new_model_df_tall[['sectors_plotting', 'sectors', 'sub1sectors','sub2sectors']].drop_duplicates().replace('x', np.nan)
    mapping = sector_plotting_mappings[['sectors_plotting', 'sectors', 'sub1sectors','sub2sectors']].drop_duplicates()
    # Merge the dataframes and add an indicator column
    merged_df = pd.merge(new_df, mapping, on=['sectors_plotting', 'sectors', 'sub1sectors','sub2sectors'], how='outer', indicator=True)
    # Find rows that are only in mapping
    missing_in_new_model = merged_df[merged_df['_merge'] == 'right_only']
    if len(missing_in_new_model) > 0:
        if RAISE_ERROR:
            raise Exception('There are sectors_plotting values that have been lost in the merge. These are: ', missing_in_new_model)
        print('There are sectors_plotting values that have been lost in the merge. These are: ', missing_in_new_model)
    #now drop the sectors	sub1sectors	sub2sectors	sub3sectors	sub4sectors	 cols
    new_model_df_tall = new_model_df_tall.drop(columns=['sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'reference_sector'])
    return new_model_df_tall

def merge_fuel_mappings(model_df_tall_sectors, new_fuel_plotting_mappings,fuel_plotting_mappings, RAISE_ERROR=True):
    #using the plotting mappings which were created in the format_plotting_mappings function, we need to merge these onto the model_df_tall using the reference_column and reference_fuel columns, where the reference column specifies the column to find the reference fuel in the model_df_tall. This is the same as the merge_sector_mappings function, But importantly, the result from merge_sector_mappings is used instead of the model_df_tall, and so the output of this will contain the sectors_plotting column
    #now we join on the fuels mappigns:
    new_new_model_df_tall = model_df_tall_sectors.copy()
    #empty it
    new_new_model_df_tall = new_new_model_df_tall[0:0]
    #so join the new_fuel_plotting_mappings to the model_df_tall
    for unique_col in new_fuel_plotting_mappings.reference_column.unique():
        columns_data = new_fuel_plotting_mappings[new_fuel_plotting_mappings.reference_column == unique_col][['fuels_plotting', 'reference_fuel']]
        #filter for the unique col and then join on the unique col to the model_df_tall
        columns_data = model_df_tall_sectors.merge(columns_data, how='inner', left_on=unique_col, right_on='reference_fuel')
        #concat to the new_model_df_tall
        new_new_model_df_tall = pd.concat([new_new_model_df_tall, columns_data])
    #and to be more precise, check the uniqe rows for the columns [[fuels_plotting	fuels	subfuels]] in the fuels_mappings are all in the new_new_model_df_tall
    
    new_df = new_new_model_df_tall[['fuels_plotting', 'fuels', 'subfuels']].drop_duplicates().replace('x', np.nan)
    mapping = fuel_plotting_mappings[['fuels_plotting', 'fuels', 'subfuels']].drop_duplicates()
    # Merge the dataframes and add an indicator column
    merged_df = pd.merge(new_df, mapping, on=['fuels_plotting', 'fuels', 'subfuels'], how='outer', indicator=True)
    # Find rows that are only in mapping
    missing_in_new_model = merged_df[merged_df['_merge'] == 'right_only']
    if len(missing_in_new_model) > 0:
        if RAISE_ERROR:
            raise Exception('There are fuels_plotting values that have been lost in the merge. These are: ', missing_in_new_model)
        print('There are fuels_plotting values that have been lost in the merge. These are: ', missing_in_new_model)#This could be because they dont match any original categories, or *unlikely* they arent used by any of the sectors referenced in sectors plotting
    
    #drop the fuels cols
    new_new_model_df_tall = new_new_model_df_tall.drop(columns=['fuels', 'subfuels','reference_fuel'])
    
    #drop duplicates
    new_new_model_df_tall = new_new_model_df_tall.drop_duplicates()
    return new_new_model_df_tall


def merge_transformation_sector_mappings(model_df_tall, transformation_sector_mappings,new_fuel_plotting_mappings, RAISE_ERROR=True):
    #the input_fuel col is a bool and determines whether we are looking for input or output fuels from the transformation sector. If input then the values need to be negative, if output then positive (We'll filter for this)

    #we will create a new dataframe which is the aggregation of the sectors in the transformation_sector_mappings dataframe, applied to the 9th modelling data. 
    #we will create a column within this dataframe called sectors_plotting which will then be able to be stacked with the other columns in other dataframes with the same column name

    model_df_transformation = model_df_tall.copy()
    #join the transformation_sector_mappings dataframe to the model_df_tall_transformation dataframe
    model_df_transformation = model_df_transformation.merge(transformation_sector_mappings, how='right', on=['sectors','sub1sectors'])

    #and join the fuel_plotting mapping to the df 
    new_model_df_transformation = model_df_transformation.copy()
    #empty it
    new_model_df_transformation = new_model_df_transformation[0:0]

    #so join the new_sector_plotting_mappings to the model_df_tall
    for unique_col in new_fuel_plotting_mappings.reference_column.unique():
        columns_data = new_fuel_plotting_mappings[new_fuel_plotting_mappings.reference_column == unique_col][['fuels_plotting', 'reference_fuel']]
        #filter for the unique col and then join on the unique col to the model_df_tall
        columns_data = model_df_transformation.merge(columns_data, how='inner', left_on=unique_col, right_on='reference_fuel')
        #concat to the new_model_df_tall
        new_model_df_transformation = pd.concat([new_model_df_transformation, columns_data])
    
    #now separaten into input and output dfs using the boolean and whtehr value is positive or negative
    input_transformation = new_model_df_transformation[(new_model_df_transformation['input_fuel'] == True) & (new_model_df_transformation['value'] < 0)]

    output_transformation = new_model_df_transformation[(new_model_df_transformation['input_fuel'] == False) & (new_model_df_transformation['value'] > 0)]
    
    
    #check that no sectors_plotting values from transformation_sector_mappings have been lost
    new_df = new_model_df_transformation[['sectors_plotting', 'sectors', 'sub1sectors']].drop_duplicates().replace('x', np.nan)
    mapping = transformation_sector_mappings[['sectors_plotting', 'sectors', 'sub1sectors']].drop_duplicates() 
    # Merge the dataframes and add an indicator column
    merged_df = pd.merge(new_df, mapping, on=['sectors_plotting', 'sectors', 'sub1sectors'], how='outer', indicator=True)
    # Find rows that are only in mapping
    missing_in_new_model = merged_df[merged_df['_merge'] == 'right_only']
    if len(missing_in_new_model) > 0:
        if RAISE_ERROR:
            raise Exception('There are sectors_plotting values that have been lost in the merge. These are: ', missing_in_new_model)
        print('There are sectors_plotting values that have been lost in the merge. These are: ', missing_in_new_model)
    
    #drop the fuels cols
    new_model_df_transformation = new_model_df_transformation.drop(columns=['fuels', 'subfuels','reference_fuel'])
    
    return input_transformation, output_transformation

# def collect_missing_datapoints(economy_new_charts_mapping):
#     #now loop through the unique sheet, table combinations and idneitfy if there are any missing values (nas) in the value col. Put the data for these into a new dataframe called missing_data
#     missing_data = pd.DataFrame()
#     na_data = economy_new_charts_mapping[economy_new_charts_mapping.value.isna()]
#     for table_id in economy_new_charts_mapping.table_id.unique():
#         if table_id in na_data.table_id.unique():
#             missing_data = pd.concat([missing_data, na_data[na_data.table_id == table_id]])
#     return missing_data, economy_new_charts_mapping

# def check_for_duplicates_in_plotting_names(new_sector_plotting_mappings, new_fuel_plotting_mappings, RAISE_ERROR=True):
#     #this is important because??
    
#     plotting_names = new_sector_plotting_mappings['sectors_plotting'].unique().tolist() + new_fuel_plotting_mappings['fuels_plotting'].unique().tolist()
#     #identify if there are any duplicates in the plotting names
#     duplicates = [item for item, count in collections.Counter(plotting_names).items() if count > 1]
#     if len(duplicates) > 0:
#         if RAISE_ERROR:
#             raise Exception('There are plotting names that are duplicated between fuels and sectors. Please check the following plotting names: ', duplicates)
#         else:
#             print('There are plotting names that are duplicated between fuels and sectors. You might want to check the following plotting names: ', duplicates)

#     return set(plotting_names)
    
def test_plotting_names_match_charts_mapping(plotting_names,new_charts_mapping):
    #double check teh unique plotting anmes in both new_charts_mapping and plotting_df are exactly the same otherwise, if there are any plotting names in new_charts_mapping that are not in plotting_df then we will have a problem, and if there are any plotting names in plotting_df that are not in new_charts_mapping then we should let the user know in case they want to remove them from the plotting_df
    new_charts_mapping_names = set(new_charts_mapping.plotting_column.unique())
    if len(plotting_names) > len(new_charts_mapping_names):
        different_names = plotting_names - new_charts_mapping_names
        print('there are plotting names in the sectors, fuels or transformations mappings that are not in new_charts_mapping. These are:\n ', different_names, '\n This is not an immediate problem, but you may want to remove them from the plotting_df if its getting cluttered.')
    elif len(plotting_names) < len(new_charts_mapping_names):
        different_names = new_charts_mapping_names - plotting_names
        raise ValueError('there are plotting names in new_charts_mapping that are not in the sectors, fuels or transformations mappings. These are: \n', different_names)
    else:
        pass
        
def test_plotting_names_match_colors_df(plotting_names,colors_df):
    #also check that colors_df.Plotting_name is the same as plotting_df.plotting_name
    colors_plotting_names = set(colors_df.plotting_name.unique())
    if len(plotting_names) > len(colors_plotting_names):
        different_names = plotting_names - colors_plotting_names
        raise ValueError('there are plotting names in plotting_df that are not in colors_df. These are:\n ', different_names)
    elif len(plotting_names) < len(colors_plotting_names):
        different_names = colors_plotting_names - plotting_names
        print('there are plotting names in colors_df that are not in plotting_df. These are:\n ', different_names)
    else:
        pass 
        
# def prepare_color_plot(colors_df):

#     # Create labels and colors lists
#     labels = colors_df.plotting_name
#     colors = colors_df.color

#     #identify any duplicate labels
#     if labels[labels.duplicated()].empty == False:
#         raise ValueError('Duplicate labels found in the colors_df dataframe', labels[labels.duplicated()])
    
#     #create dict
#     colors_dict = dict(zip(labels, colors))
    
#     plot_color_grid(colors_dict)
#     plot_color_wheel(colors_dict)
    
# def plot_color_wheel(colors_dict):
    
#     #Convert to the HSV color space and sort by hue:
#     # Function to convert hex color to RGB
#     def hex_to_rgb(hex_color):
#         hex_color = hex_color.lstrip('#')
#         return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))

#     # Function to convert RGB color to HSV
#     def rgb_to_hsv(rgb_color):
#         return colorsys.rgb_to_hsv(*rgb_color)

#     # Convert colors to HSV and create a list of (label, color, hsv) tuples
#     color_tuples = [(label, color, rgb_to_hsv(hex_to_rgb(color))) for label, color in colors_dict.items()]

#     # Sort by hue
#     color_tuples.sort(key=lambda x: x[2][0])

#     # Create labels and colors lists from sorted tuples
#     labels = [t[0] for t in color_tuples]
#     colors = [t[1] for t in color_tuples]

#     # Create an array of angles evenly spaced around a circle
#     angles = np.linspace(0, 2 * np.pi, len(labels) + 1)

#     # Create a trace for the polar chart
#     trace = go.Barpolar(
#         r=[1] * len(labels),  # All bars have the same length
#         theta=angles * 180 / np.pi,  # Convert angles to degrees
#         width=[np.diff(angles)[0]] * len(labels),  # All bars have the same width
#         marker=dict(color=colors),
#         text=labels,
#         hoverinfo='text',
#         showlegend=False
#     )

#     # Create the layout for the plot
#     layout = go.Layout(
#         title='Color Wheel Representation',
#         polar=dict(
#             radialaxis=dict(visible=False),
#             angularaxis=dict(visible=False),
#         ),
#         paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
#     )

#     # Create the figure and add the trace
#     fig = go.Figure(data=[trace], layout=layout)

#     # write the figure to html
#     fig.write_html("../config/plotting_names_color_wheel.html")
    
    
# def plot_color_grid(colors_dict):
        
#     # Determine grid size based on number of colors
#     n = len(colors_dict)
#     cols = round(math.sqrt(n))
#     rows = cols if cols * cols >= n else cols + 1

#     # Create subplot matrix with invisible plots
#     fig = make_subplots(rows=rows, cols=cols)

#     # Create labels and colors lists
#     labels = list(colors_dict.keys())
#     colors = list(colors_dict.values())

#     # Fill subplots with colors
#     for i in range(rows):
#         for j in range(cols):
#             index = i * cols + j
#             if index < n:
#                 fig.add_trace(
#                     go.Scatter(x=[0, 1], y=[0, 1], mode='text',
#                             text=[labels[index]], showlegend=False,
#                             textposition='middle center'),
#                     row=i + 1, col=j + 1
#                 )
#                 fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, visible=False, row=i + 1, col=j + 1)
#                 fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, visible=False, row=i + 1, col=j + 1)
#                 fig.add_layout_image(
#                     dict(
#                         source="data:image/svg+xml;base64,CiAgPHN2ZyB3aWR0aD0iMCIgaGVpZ2h0PSIwIj4KICAgIDxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiN7fSIvPgogIDwvc3ZnPgo=".format(colors[index]),
#                         xref="x{}".format(index+1),
#                         yref="y{}".format(index+1),
#                         x=0,
#                         y=1,
#                         sizex=1,
#                         sizey=1,
#                         sizing="stretch",
#                         layer="below"
#                     )
#                 )
#     # write the figure to html
#     fig.write_html("../config/plotting_names_color_grid.html")