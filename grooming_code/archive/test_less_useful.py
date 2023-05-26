
#################################
#in fuels_used_by_modellers we have all the fuels the modellers specified as being useful for their model. We will use this to categorise and identify what fuels are used in each sector. We can use this to identify if a new fuel is being used in a sector or if a fuel is no longer being used in a sector.
#we will extract the data and save it to a csv file in intermediate data
#note that the columns: 'Industry and non-energy', 'Transport', 'Buildings', 'Hydrogen', 'Ag, fish & non-spec', 'Power', 'Refining (oil & biofuels)','Supply' contains either 'a', '?' or NAN. The 'a' indicates that the fuel is used in the sector. The '?' indicates that the fuel is might be used in the sector. The NAN indicates that the fuel is not used in the sector. For the ?'s we should assume it is not and then print a warning if it is used in the sector.
#the columns 'Industry and non-energy.1', 'Transport.1', 'Buildings.1', 'Hydrogen.1', 'Ag, fish & non-spec.1', 'Power.1', 'Refining (oil & biofuels).1', 'Supply.1' contain the fuel names. THis doesnt seem useful yet.

#we will create a dataframe with the following columns: sector, fuel. Then it can be used to check if a new fuel is being used in a sector or if a fuel is no longer being used in a sector.

#first drop non useful columns
fuels_used_by_modellers = fuels_used_by_modellers[['FUELS', 'Industry and non-energy', 'Transport', 'Buildings', 'Hydrogen', 'Ag, fish & non-spec', 'Power', 'Refining (oil & biofuels)','Supply']]
#these are the sectors for which we have different models^. If a fuel is used by one of these modellers and its not in this list then we should print a warning
#convert values in cols to booleans:
for col in fuels_used_by_modellers.columns[1:]:
    fuels_used_by_modellers[col] = fuels_used_by_modellers[col].apply(lambda x: True if x == 'a' else False)

#now melt so we have a row for each sector fuel combination and then remove rows where the fuel is not used in the sector (i.e. where the value is False)
fuels_used_by_modellers = pd.melt(fuels_used_by_modellers, id_vars=['FUELS'], value_vars=['Industry and non-energy', 'Transport', 'Buildings', 'Hydrogen', 'Ag, fish & non-spec', 'Power', 'Refining (oil & biofuels)','Supply'], var_name='sector', value_name='fuel_used')

#now remove rows where fuel_used is False
fuels_used_by_modellers = fuels_used_by_modellers[fuels_used_by_modellers['fuel_used'] == True]

#drop thje fuel_used column
fuels_used_by_modellers = fuels_used_by_modellers.drop('fuel_used', axis=1)

#rename FUELS to fuels
fuels_used_by_modellers = fuels_used_by_modellers.rename(columns={'FUELS':'fuel'})

#save as csv
fuels_used_by_modellers.to_csv(f'../intermediate_data/config/fuels_used_by_modellers_{FILE_DATE_ID}.csv', index=False)
#great.

###############



#Cxreate a list of dictionaries which will contain keys: sheet_name, column_name, old_value, new_value
changes_list = []
changes_list.append({'sheet_name':'Power fuel consumption', 'column_name':'Transformation', 'old_value':'Input fuel', 'new_value':'Power'})
#but now how to do the refinery output and input? Might need to name new_value either refinery input or refinery output 
changes_list.append({'sheet_name':'Refining', 'column_name':'Transformation', 'old_value':'Input to refinery', 'new_value':'Refinery'})
changes_list.append({'sheet_name':'Refining', 'column_name':'Transformation', 'old_value':'Output from refinery', 'new_value':'Refinery'})#ASSUMPTION: WE CAN USE THE SAME NAME FOR BOTH INPUT AND OUTPUT AS WE CAN IDENTIFY WHICH IS WHICH BASED ON IF THE VALUE IS POSTIVE (OUTPUT) OR NEGATIVE (INPUT)
# changes_list.append({'sheet_name':'Heat only consumption', 'column_name':'Transformation', 'old_value':'Refinery output', 'new_value':'Refinery output'})#empty workbook
changes_list.append({'sheet_name':'Hydrogen', 'column_name':'TECHNOLOGY', 'old_value':'Input fuel', 'new_value':'Hydrogen'})

#what about Own-use and losses. and exports.
###############

#now we will loop through the table_tuple and first try to rename the columns based on the unique_categories. then where anything cannot be mapped, leave it
table_tuple_columns_mapped = ()
excludeable_cols = ['sheet', 'unit', 'table_number', 'Economy']
for table_group in table_tuple:
    for col in table_group.columns:
        COL_FOUND = False
        if col in excludeable_cols:
            continue
        #find the first value in the column and find if it is in a column in unique_categories
        value_to_find = table_group[col].dropna().iloc[0]
        #now find if it is in any of the columns in unique_categories
        for unique_category in unique_categories.columns:
            if value_to_find in unique_categories[unique_category].tolist():
                #now rename the column
                table_group = table_group.rename(columns={col:unique_category})
                COL_FOUND = True
                break
        if COL_FOUND == False:
        #print that we couldnt find it and what the value and column name is
            print('Couldnt find value: ' + value_to_find + ' , from column: ' + col)

    #now add the table_group to the tuple
    table_tuple_columns_mapped = table_tuple_columns_mapped + (table_group,)

#######################