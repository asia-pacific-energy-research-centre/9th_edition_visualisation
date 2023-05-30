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

#first we import the transformation mappigns from the visualisation_category_mappings.xlsx file
transformation_sector_mappings = pd.read_excel('../config/visualisation_category_mappings.xlsx', sheet_name='transformation_sector_mappings')
#Index(['input_fuel', 'sectors_plotting', 'sectors','sub1sectors'], dtype='object')

#for now jsut use the sheet called Balances from that file, as its where we ahve mapped the most values
charts_mapping = pd.read_excel('../intermediate_data/config/charts_mapping_9th_computer_generated.xlsx', sheet_name='Balances')

##############################################################################

#take in the model_variables.xlsx file and check that the unique variables in the columns in Variables sheet match the variables in the columns in the Data sheet. If not, throw a descriptive error/warning.

model_variables = pd.read_excel('../input_data/model_variables.xlsx', sheet_name='Variables', header = 2)
#############################
#FORMAT THE MAPPINGS
#for fuel and sector mappings we will extract the most sepcific reference for each row and then record it's column in a column called 'column'.
#so for example, where we want to extract the reference for the sectors_plotting value Agriculture, we find the rightmost column that is not na (this is the msot specific column), set 'reference_sector' to that value in the most specific column, and then the column to the name of the most specific column
new_sector_plotting_mappings = pd.DataFrame(columns=['sectors_plotting', 'reference_sector', 'reference_column'])

ordered_columns = [ 'sub2sectors', 'sub1sectors','sectors']
for col in ordered_columns:
    #extract rows where the value is not na in this col
    for row in sector_plotting_mappings[sector_plotting_mappings[col].notna()].index:
        #loop through the rows
        row_x = sector_plotting_mappings.loc[row]
        #create new row in new_sector_plotting_mappings
        new_sector_plotting_mappings = new_sector_plotting_mappings.append({'sectors_plotting': row_x['sectors_plotting'], 'reference_sector': row_x[col], 'reference_column': col}, ignore_index=True)
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
        new_fuel_plotting_mappings = new_fuel_plotting_mappings.append({'fuels_plotting': row_x['fuels_plotting'], 'reference_fuel': row_x[col], 'reference_column': col}, ignore_index=True)
    #remove these rows from the sector_plotting_mappings so that we don't double count them
    fuel_plotting_mappings = fuel_plotting_mappings[fuel_plotting_mappings[col].isna()]

#now check for nas in the entire dfs
if new_sector_plotting_mappings.isna().sum().sum() > 0:
    data_checking_warning_or_error('There are still some nas in the new_sector_plotting_mappings')
if new_fuel_plotting_mappings.isna().sum().sum() > 0:
    data_checking_warning_or_error('There are still some nas in the new_fuel_plotting_mappings')


charts_mapping = charts_mapping.drop(columns=['fuels_8th', 'sectors_8th'])
#concat unique sheet and table_numbers cols
charts_mapping['table_id'] = charts_mapping['sheet'] + '_' + charts_mapping['table_number'].astype(str)
#save in intermediate data for use in ????
# new_sector_plotting_mappings.to_csv(f'../intermediate_data/config/plotting_sector_mappings_{FILE_DATE_ID}.csv', index=False)
# new_fuel_plotting_mappings.to_csv(f'../intermediate_data/config/plotting_fuel_mappings_{FILE_DATE_ID}.csv', index=False)
# transformation_sector_mappings.to_csv(f'../intermediate_data/config/transformation_sector_mappings_{FILE_DATE_ID}.csv', index=False)

#############################
#PROCESS THE DATA
#############################

#because we have issues with data being too large, we will run through each eocnomy in the model_df_wide and save it as a pickle separately.
for economy_x in model_df_wide['economy'].unique():
    model_df_wide_economy = model_df_wide[model_df_wide['economy'] == economy_x]
    # #TEMP
    # #filter for reference scenarios
    # model_df_wide_economy = model_df_wide_economy[model_df_wide_economy['scenarios'] == 'reference']
    # #filter for 01_AUS economy
    # model_df_wide_economy = model_df_wide_economy[model_df_wide_economy['economy'] == '01_AUS']
    
    #make model_df_wide_economy into model_df_tall
    #fgirst grab object copls as the index cols
    index_cols = model_df_wide_economy.select_dtypes(include=['object']).columns
    #now melt the data
    model_df_tall = pd.melt(model_df_wide_economy, id_vars=index_cols, var_name='year', value_name='value')
    

    #data details:
    #Columns: model_df_wide_economy.columns
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
        if len(diff) > 0:
            #determine whether its missing from the Variables sheet or the Data sheet
            for variable in diff:
                #skip the economy column
                if col == 'economy':
                    continue
                elif variable in unique_variables:
                    data_checking_warning_or_error('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))
                else:
                    data_checking_warning_or_error('The variable {} in the column {} is missing from the Data sheet'.format(variable, col))

    #############################
    #EXTRACT PLOTTING NAMES FROM MODEL DATA
    #and now these mappings can be joined to the model_df and used to extract the data needed for each plotting_name
    #note that (i think) it works if you :
    # copy model df tall. called it sector_model_df_tall
    # in sector_model_df_tall join the sector plotting names (left join).  #note this will need to be done a special way because its no simple join
    # remove the sector columns. 
    ####DROPPED THESE BELOW
    # copy model df tall again, called it sector_blank
    # in sector_blank, remove the sector columns and create new sector_plotting column and fill it with np.nan #this allows for when the graph might not need a sectort. but tbh would expect it to need at least sector = total?
    # stack sector_blank on sector_model_df_tall
    ####DROPPED THESE ABOVE
    # join fuels_plotting to sector_model_df_tall using left join?   #note this will need to be done a special way because its no simple join
    #drop the other fuels columns

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

    #now drop the sectors	sub1sectors	sub2sectors	sub3sectors	sub4sectors	 cols
    new_model_df_tall = new_model_df_tall.drop(columns=['sectors', 'sub1sectors', 'sub2sectors', 'sub3sectors', 'sub4sectors', 'reference_sector'])

    #now we join on the fuels mappigns:
    
    new_new_model_df_tall = new_model_df_tall.copy()
    #empty it
    new_new_model_df_tall = new_new_model_df_tall[0:0]

    #so join the new_sector_plotting_mappings to the model_df_tall
    for unique_col in new_fuel_plotting_mappings.reference_column.unique():
        columns_data = new_fuel_plotting_mappings[new_fuel_plotting_mappings.reference_column == unique_col][['fuels_plotting', 'reference_fuel']]
        #filter for the unique col and then join on the unique col to the model_df_tall
        columns_data = new_model_df_tall.merge(columns_data, how='inner', left_on=unique_col, right_on='reference_fuel')
        #concat to the new_model_df_tall
        new_new_model_df_tall = pd.concat([new_new_model_df_tall, columns_data])

    #drop the fuels cols
    new_new_model_df_tall = new_new_model_df_tall.drop(columns=['fuels', 'subfuels','reference_fuel'])

    #what about if we need sectors where fuels are blank? i dont think its liekly though? because without a definition for sector you will get double ups, for example form the sum of TFEC and TFC.

    #now we have a df with only the columns fuels_plotting and sectors_plotting which contains defintiions of all the possible combinations of fuels_plotting and sectors_plotting we could have.. i think.
    #call it plotting_df
    plotting_df = new_new_model_df_tall.copy()

    #############################
    #TRANSFORMATION MAPPING
    #next step will include creating new datasets which create aggregations of data to match some of the categories plotted in the 8th edition. 
    #for example we need an aggregation of the transformation sector input and output values to create entries for Power, Refining or Hydrogen


    #the input_fuel col is a bool and determines whether we are looking for input or output fuels from the transformation sector. If input then the values will be negative, if output then positive

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

    #drop the fuels cols
    new_model_df_transformation = new_model_df_transformation.drop(columns=['fuels', 'subfuels','reference_fuel'])
    
    #now separaten into input and output dfs using book and whtehr value is positive or negative
    input_transformation = new_model_df_transformation[(new_model_df_transformation['input_fuel'] == True) & (new_model_df_transformation['value'] < 0)]

    output_transformation = new_model_df_transformation[(new_model_df_transformation['input_fuel'] == False) & (new_model_df_transformation['value'] > 0)]

    #Thats it. We will stack this with the other dataframes later on. We wont sum up by plotting_sector yet as we will do that later on when we have all the dataframes stacked together (the extra info is usefuul right now)
    plotting_df = pd.concat([plotting_df, input_transformation, output_transformation])
    
    #sum up the values by the ?object cols? so we dont accidentally sum up by economy or somethign else. #ignore nas
    plotting_df = plotting_df.groupby(['scenarios','economy', 'year','sectors_plotting', 'fuels_plotting']).sum().reset_index()
    
    #############################
    #now we can extract the data for each graph we need to produce using the file D:\APERC\9th_edition_visualisation\intermediate_data\config\charts_mapping_9th_computer_generated.xlsx

    #for each unique sheet, table_numbers combination, extract the values form the cols sectors_8th_plotting and fuels_8th_plotting which specifies the data we need to grab from the new plotting_df
    #so drop the fuels_8th and secotrs_8th cols
    #merge these cols with the plotting_df and grab the values.
    economy_charts_mapping = charts_mapping.merge(plotting_df, how='left', left_on=['sectors_8th_plotting','fuels_8th_plotting'], right_on=['sectors_plotting','fuels_plotting'])
    #drop the cols we dont need
    economy_charts_mapping = economy_charts_mapping.drop(columns=['sectors_8th_plotting','fuels_8th_plotting'])
    #now loop through the unique table_ids and idneitfy if there are any missing values (nas) in the value col. Put the data for these into a new dataframe called missing_data
    missing_data = pd.DataFrame()
    for table_id in economy_charts_mapping.table_id.unique():
        data = economy_charts_mapping[economy_charts_mapping.table_id == table_id]
        if data.value.isna().any():
            economy_charts_mapping = economy_charts_mapping[economy_charts_mapping.table_id != table_id]
            missing_data = pd.concat([missing_data, data])
    #now we have a dataframe called missing_data which contains the data we dont have mapped, yet. We will need to map this manually. Print the unique 'sectors_plotting','fuels_plotting' in this dataframe
    if len(missing_data) > 0:
        print('There are ' + str(len(missing_data)) + ' unique sectors_plotting, fuels_plotting combinations that need to be mapped manually')
        #print the unique sectors_plotting, fuels_plotting combinations
        print(missing_data[['sectors_plotting','fuels_plotting']].drop_duplicates())
    else:
        print('There are no missing values in the plotting_df')

    #check for duplicates. not sure why there are duplicates, but there are. so drop them
    if len(economy_charts_mapping[economy_charts_mapping.duplicated()]) > 0:
        print('There are ' + str(len(economy_charts_mapping[economy_charts_mapping.duplicated()])) + ' duplicates in the economy_charts_mapping dataframe')
        economy_charts_mapping = economy_charts_mapping.drop_duplicates()
    else:
        print('There are no duplicates in the economy_charts_mapping dataframe')
    
    import plotly.express as px
    import plotly.graph_objects as go
    #since we havent gotten to specifiying the atual plot that is required, just plot a line graph with matplotlib. save it with the name being the same as the unique sheet, table_numbers combination and save it in output\plotting_output
    economy_charts_mapping['legend'] = economy_charts_mapping['sectors_plotting'] + '_' + economy_charts_mapping['fuels_plotting']
    #filter for just 2017 to 2030
    #make year an int
    economy_charts_mapping['year'] = economy_charts_mapping['year'].astype(int)
    economy_charts_mapping = economy_charts_mapping[(economy_charts_mapping.year >= 2017) & (economy_charts_mapping.year <= 2030)]
    #order years
    economy_charts_mapping = economy_charts_mapping.sort_values(by=['year'])

    #replavce 0's with nan
    economy_charts_mapping['value'] = economy_charts_mapping['value'].replace(0, np.nan)
    #since we are missing data up to 2030, do a ffill on 0's, grouped by the table_id, economy, scenario, sectors_plotting, fuels_plotting cols
    economy_charts_mapping['value'] = economy_charts_mapping.groupby(['table_id','economy','scenarios','sectors_plotting','fuels_plotting'])['value'].ffill()

    #also, because of 
    
    j=0
    plot_this = False
    if plot_this:
        #loop through the unique table_ids, but stop after plotting the first one for now
        for i, table_id in enumerate(economy_charts_mapping.table_id.unique()):
            # if i > 0:
            #     break
            data = economy_charts_mapping[economy_charts_mapping.table_id == table_id]


            #for each economy and scenario, plot a line graph
            for economy in data.economy.unique():
                for scenario in data.scenarios.unique():
                    # j+=1
                    # print(j)

                    #filter for the economy and scenario
                    plot_data = data[(data.economy == economy) & (data.scenarios == scenario)]
                    #plot the data so the x axis is year and the y axis is value then make the legend the legend col
                    fig = px.line(plot_data, x="year", y="value", color='legend', title=table_id + ' ' + economy + ' ' + scenario)
                    #format the x axis years
                    fig.update_xaxes(tickvals=[2017, 2020, 2025, 2030])
                    #make the y axis the value with the unit as the label
                    fig.update_yaxes(title_text=data.unit.unique()[0])

                    #save the plot as html
                    fig.write_html('../output/plotting_output/' + table_id + '_' + economy + '_' + scenario + '.html')

                    #also save the data to a csv in wide format so we can see what the data looks like
                    plot_data.to_csv('../output/plotting_output/csvs/' + table_id + '_' + economy + '_' + scenario + '.csv', index=False)
                    
                

    
    #############################
    #save data to pickle
    plotting_df.to_pickle(f'../intermediate_data/data/data_mapped_to_plotting_names_9th_{economy_x}_{FILE_DATE_ID}.pkl')
    #and sav economy_charts_mapping to pickle since its useful
    economy_charts_mapping.to_pickle(f'../intermediate_data/data/economy_charts_mapping_9th_{economy_x}_{FILE_DATE_ID}.pkl')
    

    #what next? 
    # i guess we need to introduce more ability to edit graphs and choose how theyll be presented. eg. title, colors, graph stylew (bar vs line etc), total vvs no total, better legend names, better axis names, better axis labels, better axis units, better axis scales, better axis limits, better axis ticks, better axis tick labels, better axis tick units, better axis tick scales, better axis tick limits, better axis tick po
    # It would also be good to get the 8th data in here so we can compare against that.
    # it would be good to create the same format as the workbook in the 8th data so we could move to doing that
#%%