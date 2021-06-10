import pandas as pd
import requests
import re
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_colwidth', 0)

class MarkeyDataTools:
    # first, it stores the key (I think the key is not really required...)
    # For now, the available regions is state, county, county subdivision and tract.
    # I can add more if needed
    def __init__(self, key = None):
        if key == None:
            self.insert_key()
        else:
            self.key = key
        self.census_available_region = np.array(['state','county','county subdivision','tract'])
        self.tables_basket = None
        
    def insert_key(self):
        try:
            print(self.key)
        except:
            self.key = str(input('insert your private key for the census data : '))
        
        
    # This doesn't really do much thing, but when the user defines ths region argument, 
    # I want to make sure that they are in the list self.census_available_region 
    def find_census_region(self, search_value):
        pattern = re.compile(f'{search_value}$', flags = re.I)
        index = list(map(lambda x: bool(re.search(pattern, x)), self.census_available_region))
        return(self.census_available_region[index][0])
    
    
    # With the given year, it provides the list of variable groups contained in the acs5 dataset
    # It also shows the variable groups contained in the acs5/profile dataset.
    def get_acs_groups(self, year):
        response_acs5 = requests.get(f'https://api.census.gov/data/{year}/acs/acs5/groups')
        response_profile = requests.get(f'https://api.census.gov/data/{year}/acs/acs5/profile/groups')
        try:
            response_acs5.raise_for_status()
            response_profile.raise_for_status()
        except:
            print('check the group json website')
        acs5 = pd.DataFrame(response_acs5.json()['groups'])
        profile = pd.DataFrame(response_profile.json()['groups'])
        acs5['source'] = 'acs5'
        profile['source'] = 'profile'
        groups = pd.concat([acs5, profile], ignore_index = True)
        groups = groups.iloc[:, [0,1,3]]
        self.groups = groups
        
        
        
    def gen_acs_groups(self, year):
        response_acs5 = requests.get(f'https://api.census.gov/data/{year}/acs/acs5/groups')
        response_profile = requests.get(f'https://api.census.gov/data/{year}/acs/acs5/profile/groups')
        try:
            response_acs5.raise_for_status()
            response_profile.raise_for_status()
        except:
            print('check the group json website')
        acs5 = pd.DataFrame(response_acs5.json()['groups'])
        profile = pd.DataFrame(response_profile.json()['groups'])
        acs5['source'] = 'acs5'
        profile['source'] = 'profile'
        groups = pd.concat([acs5, profile], ignore_index = True)
        groups = groups.iloc[:, [0,1,3]]
        self.groups = groups

        
        
    def drop(self, dataframe, colname, group = False):
        if group:
            pattern = re.compile(colname, flags = re.I)
            colname = dataframe.columns.to_series()
            index = colname.str.match(pattern)
            colname_to_drop = colname[index]
            return(dataframe.drop(colname_to_drop))
        else:
            return(dataframe.drop(colname))

      

    
    def gen_pattern(self, subgroup_type):
        if subgroup_type.lower() == 'sex':
            pattern = re.compile('.*sex.*', flags = re.I)
        elif subgroup_type.lower() == 'age':
            pattern = re.compile('.*age.*', flags = re.I)
        elif subgroup_type.lower() == 'both':
            pattern = re.compile('(?=.*sex.*)(?=.*age.*)', flags = re.I)
        else:
            pattern = None
        return(pattern)
            
class acs(MarkeyDataTools):
    def __init__(self, Key = None):
    # Run the init function of the parent class first
        super().__init__(key = Key)

        



    def __repr__(self):
        message = 'This module is to pull and search the American Community Survey Data; for more information, please visit https://github.com/leeparkuky/MarkeyDataTools'      
        return(message)

    def guide(self):
        year = int(input('what year was the dataset created:'))
        group = ""
        groups = []
        while group.lower() != "quit": 
            group = str(input('provide a group name to include in your dataset [when you finished, please submit "quit"'))
            groups.append(group)
        acs = 'acs5'
        response = str(input('Is the dataset "acs5"? [Yes/No]'))
        if response.lower() == 'no':
            acs = str(input('What is the dataset of interest:'))
        geo_response = str(input('What is the geological level? [State, County, County Subdivision, Tract] :'))
        self.insert_inputs(year, table = groups, source = acs, region = geo_response)


    def update_inputs(self, year = None, table = None, region = None, source = None):
        if year == None:
            pass
        else:
            self.year = year
        
        if table == None:
            pass
        else:
            if type(table) == str:
                table = self.find_variable_list(table)
            elif type(table) == list:
                table = pd.concat((list(map(self.find_variable_list, table))))
            self.table_list = table
                
        if region == None:
            pass
        else:
            self.region = self.find_census_region(region)
        
        self.gen_group_variable_desc(self.table_list)
        if source == None:
            pass
        else:
            self.source = source
        
        
        
        
        
    def insert_inputs(self, year, table, source = 'acs5', state = 'KY', region = 'County'):
    # assign values to the following attributes
        self.year = year
        
        
    # complying with the API syntax for the sources.
        if bool(re.match('acs/acs\d', source)):
            pass
        elif bool(re.match('acs\d', source)):
            source = '/'.join(['acs', source])
        self.source = source
        
    # generating the variable table first
        self.gen_variable_table()
        
    # table names has to follow the syntax for the API call
        if type(table) == str:
            table = self.find_variable_list(table)
        elif type(table) == list:
            table = pd.concat((list(map(self.find_variable_list, table))))

            
#         var_name = ','.join(names)
#         return(var_name)            
            
    # For some reason, it sometimes generate multiple ,'s at the end
    # This should be substituted with a blank.
#         pattern = re.compile(',,+')
#         table = re.sub(pattern, '', table)   
        self.table_list = table


    # If the state is Kentucky, the FIPS code 21;
    # Otherwise, it is not going to run
        if state == 'KY':
            self.state = 21
        else:
            print('for now, it works only for the state of Kentucky')


    # cleaning region
        self.region = self.find_census_region(region)
        self.gen_group_variable_desc(self.table_list)
    # generate the variable table
        self.gen_variable_table()

    def acs5_variables(self):
        try:
            (self.year)
        except:
            self.year = 2019
        response = requests.get(f'https://api.census.gov/data/{self.year}/acs/acs5/variables')
        lists = response.json()
        header , values = lists[0], lists[1:]
        return(pd.DataFrame(values, columns = header))
    
    

        
    def sub_group_search(self, keyword_regex = None):
        try:
            self.year
        except:
            self.year = 2019
        response = requests.get(f'https://api.census.gov/data/{self.year}/acs/acs5/subject/groups')
        json = response.json()['groups']
        table = pd.DataFrame(json).sort_values('name').reset_index(drop = True)
        if keyword_regex == None:
            return(table)
        else:
            pattern = re.compile(f'.*({keyword_regex}).*', flags = re.I)
            finding = table.loc[table.description.str.match(pattern),:]
            return(finding)
        
    def group_search(self, keyword_regex = None, B = True, subgroups = None):
        '''possible choices of subgroups are sex, age, and both'''#################################################################
        try:
            self.year
        except:
            self.year = 2019
        pattern = re.compile(f'(\s+({keyword_regex}).*)|(^({keyword_regex}).*)', flags = re.I)
        if subgroups == None:
            subgroups_pattern = re.compile('.*')
        else:
            subgroups_pattern = self.gen_pattern(subgroups)
        try:
            group_number = self.sub_group_search(keyword_regex).name.str.slice(1, 3).iloc[0,]
        except:
            if subgroups == None:
                name_pattern = re.compile('B.*00[123]$')
            else:
                name_pattern = re.compile('B\d+$')
            response = requests.get(f'https://api.census.gov/data/{self.year}/acs/acs5/groups')
            json = response.json()['groups']
            table = pd.DataFrame(json).sort_values('name').reset_index(drop = True)
            if keyword_regex == None:
                if B:
                    table = table.loc[table.name.str.match(name_pattern),:]
                return(table)
            else:
                pattern = re.compile(f'.*({keyword_regex}).*', flags = re.I)
                if B:
                    finding = table.loc[table.name.str.match(name_pattern)&table.description.str.match(pattern)&table.description.str.match(subgroups_pattern),:]
                else:
                    finding = table.loc[table.description.str.match(pattern)&table.description.str.match(subgroups_pattern),:]
                return(finding)
        else:
            group_number = self.sub_group_search(keyword_regex).name.str.slice(1, 3).iloc[0,]
            name_pattern = re.compile(f'B{group_number}\d+$')
            response = requests.get(f'https://api.census.gov/data/{self.year}/acs/acs5/groups')
            json = response.json()['groups']
            table = pd.DataFrame(json).sort_values('name').reset_index(drop = True)
            if keyword_regex == None:
                if B:
                    table = table.loc[table.name.str.match(name_pattern)&table.description.str.match(subgroups_pattern),:]
                return(table)
            else:
                pattern = re.compile(f'.*({keyword_regex}).*', flags = re.I)
                if B:
                    finding = table.loc[table.name.str.match(name_pattern)&table.description.str.match(pattern)&table.description.str.match(subgroups_pattern),:]
                else:
                    finding = table.loc[table.description.str.match(pattern)&table.description.str.match(subgroups_pattern),:]
                return(finding)
        
        
    
    # This generates the variable table for the source of the data
    def gen_variable_table(self):
        try:
            a = self.source
        except:
            self.source = 'acs/acs5'
            
        response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}/variables')
        lists = response.json()
        header, values = lists[0], lists[1:]
        self.variable_table =  pd.DataFrame(values, columns = header)

        
        
        
    # From the variable table, this function allows you to find relevant variables from the 'table' argument you set up.
    def find_variable_list(self, var_name):
        pattern = re.compile(f'{var_name}\_.*')
        sub_variables = self.variable_table.loc[self.variable_table.name.str.match(pattern),:]
        size = sub_variables.shape[0]
        names = sub_variables.name
        return(names)


    
    def refresh(self):
        self.acs_data = self.acs_data.sort_values('FIPS').reset_index(drop = True)
        
        
        
    # This generates the data frame using the arguments
    def gen_dataframe(self, return_table = False):
        n = 49
        if self.table_list.shape[0] > n:
            i = int(np.floor(self.table_list.shape[0]/n))
            for j in range(i+1):
                if j < i:
                    table = self.table_list[n*j:n*(j+1)]
                    table = ','.join(table)
                    pattern = re.compile(',,+')
                    table = re.sub(pattern, '', table)
                    if j == 0:
                        result = self.gen_single_frame(table)
                    else:
                        result.merge(self.gen_single_frame(table), on = 'FIPS' )
                else:
                    table = self.table_list[n*j:]
                    table = ','.join(table)
                    pattern = re.compile(',,+')
                    table = re.sub(pattern, '', table)
                    result.merge(self.gen_single_frame(table), on = 'FIPS' )
            self.acs_data = result
            self.colname = self.acs_data.columns
            
        else:
            table = self.table_list
            table = ','.join(table)
            pattern = re.compile(',,+')
            table = re.sub(pattern, '', table)   
            self.acs_data = self.gen_single_frame(table)
            self.colname = self.acs_data.columns
        
        if return_table:
            return(self.acs_data)
        
        
        
        
        
    def gen_single_frame(self, table):
        if self.region == 'state':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get={table}&for=state:{self.state}&key={self.key}')
        elif self.region == 'county':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get=NAME,{table}&for=county:*&in=state:{self.state}&key={self.key}')
        elif self.region == 'county subdivision':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get=NAME,{table}&for=county%20subdivision:*&in=state:{self.state}&in=county:*&key={self.key}')
        elif self.region == 'tract':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get=NAME,{table}&for=tract:*&in=state:{self.state}&in=county:*&key={self.key}')
        else:
            print('The region level is not found in the system')

        # separate the header and the values in the list of lists
            
        header = response.json()[0]
        values = response.json()[1:]
        df = pd.DataFrame(values, columns = header)
            
        if self.region == 'state':
            df.drop(['state'], axis = 1, inplace = True)       

        elif self.region == 'county':
            df['FIPS'] = df.state + df.county
            df.drop(['state','county'], axis = 1, inplace = True)
            df[['County', 'State']] = df.NAME.str.split(pat = ',', expand = True)
            df.drop('NAME', axis = 1, inplace = True)
            colnames = pd.concat([pd.Series(df.columns[-3:]), pd.Series(df.columns[:-3])])
            df = df[colnames]

        elif self.region == 'county subdivision':
            df['FIPS'] = df['state'] + df['county'] + df['county subdivision']
            df.drop(['state','county', 'county subdivision'], axis = 1, inplace = True)
            df[['County Subdivision', 'County', 'State']] = df.NAME.str.split(pat = ',', expand = True)
            df.drop('NAME', axis = 1, inplace = True)
            colnames = pd.concat([pd.Series(df.columns[-4:]), pd.Series(df.columns[:-4])])
            df = df[colnames]

        elif self.region == 'tract':
            df['FIPS'] = df['state'] + df['county'] + df['tract']
            df.drop(['state','county', 'tract'], axis = 1, inplace = True)
            df[['Tract', 'County', 'State']] = df.NAME.str.split(pat = ',', expand = True)
            df.drop('NAME', axis = 1, inplace = True)
            colnames = pd.concat([pd.Series(df.columns[-4:]), pd.Series(df.columns[:-4])])
            df = df[colnames]

        return(df)
    
    
    # You can search variable groups that might contain information of interest defined by the keyword
    # For now, when the user gives a simple string, comma indicates "OR"
    # It also accepts the regex pattern. However, users must make sure they are in the re.Pattern type
    def search(self, keyword, savefile = False, filename = ''):
        try:
            self.groups
        except:
            self.get_acs_groups(self.year)
        if type(keyword) == re.Pattern:
            self.search_result = self.groups.loc[self.groups.description.str.match(keyword), :]
        else:
            keyword = keyword.split(',')
            keyword = list(map(lambda x: '('+x+')', keyword))
            keyword = '|'.join(keyword)
            pattern = re.compile(f'.*({keyword}).*', flags = re.I)
            self.search_result = self.groups.loc[self.groups.description.str.match(pattern), :]
        self.search_result.reset_index(inplace = True)
        if savefile == True:
            if filename == '':
                filename = str(input("Please enter the filename: "))
                self.search_result.to_csv(filename, index = False)
            else:
                self.search_result.to_csv(filename, index = False)
        else:
            return(self.search_result)


    # With the given year and given group name, it will provide the description of the group
    def gen_group_variable_desc(self, group):
        try:
            self.groups
        except:
            self.gen_acs_groups(self.year)
        
        if type(group) == str:
            pattern = re.compile(f'{group}', flags = re.I)
            while self.groups.name.str.match(pattern).sum() == 0:
                group = str(input(f'{group} is not found in the acs5 dataset. \n Please check the name again and provide the correct one:'))
                pattern = re.compile(f'{group}', flags = re.I)
            search = self.variable_table.loc[self.variable_table.name.str.match(pattern),:]
            search = search.sort_values(by = 'name')
            self.group_variable_desc = search
            return(search)
        else:
            if bool(iter(group)):
                group_regex = '|'.join(map(lambda x: '(' + x + ')', group))
                pattern = re.compile(group_regex, flags = re.I)
                search = self.variable_table.loc[self.variable_table.name.str.match(pattern),:]
                search = search.sort_values(by = 'name')
                self.group_variable_desc = search
                return(search)
            else:
                group = str(input('Please provide the appropriate group keyword, i.e. B28005: '))
                pattern = re.compile(f'{group}', flags = re.I)
                while self.groups.name.str.match(pattern).sum() == 0:
                    group = str(input(f'{group} is not found in the acs5 dataset. \n Please check the name again and provide the correct one:'))
                    pattern = re.compile(f'{group}', flags = re.I)
                search = self.variable_table.loc[self.variable_table.name.str.match(pattern),:]
                search = search.sort_values(by = 'name')
                self.group_variable_desc = search
                return(search)
            
    
    def rename_group(self, sub, inplace = False):
        try:
            self.acs_data
        except:
            self.gen_dataframe()
        if type(sub) == dict: 
            colname = self.acs_data.columns.to_series()
            for key, values in sub.items():
                pattern = re.compile(values, flags = re.I)
                index = colname.str.match(pattern)
                colname[index] = colname[index].str.replace(values, key)
                if inplace:
                    self.acs_data.columns = colname
                    self.refresh()
                    return(self.acs_data)
                else:
                    data_copy = self.acs_data.copy()
                    data_copy.columns = colname
                    data_copy = data_copy.sort_values('FIPS').reset_index(drop = True)
                    return(data_copy)
        else:
            print('You should provide a dictionary for the sub argument')
            
    # This drops variables in the acs_data by the group name
    def group_drop(self,  group_name):
        self.acs_data = self.drop(self.acs_data, colname = group_name, group = True)
        
        
    def group_isel(self, groupname, variable_suffix, stack = False):
        copy = self.acs_data.copy()
        if type(groupname) == str:
            pattern = re.compile(groupname, flags = re.I)
            colname = self.colname[self.colname.str.match(pattern)].sort_values()
            colname.reset_index(drop = True, inplace = True)
            if type(variable_suffix) != np.ndarray:
                variable_suffix = np.array(variable_suffix)
            variable_suffix = variable_suffix - 1
            column_names = colname[variable_suffix]
            column_names = colname.to_numpy()
            column_names = np.append(self.colname.to_numpy()[:2], column_names)
            table = copy.loc[:, column_names]
        else:
            colname = np.array(self.colname)
            col = colname[:2]
            colname = [self.colname[self.colname.str.match(re.compile(x, flags = re.I))].sort_values().to_numpy() for x in groupname]
            if type(variable_suffix) != np.ndarray:
                variable_suffix = np.array(variable_suffix)
            variable_suffix = variable_suffix - 1
            column_names = [x[y] for x,y in zip(colname, variable_suffix)]
            N = len(column_names)
            for i in range(N):
                col = np.append(col, column_names[i])
            table = copy.loc[:, col]
        if stack:
            stacked_table = table.set_index(list(table.columns[:2])).stack().reset_index()
            stacked_col = stacked_table.columns.to_series()
            stacked_col[2:] = ['Variable', 'Values']
            stacked_table.columns = stacked_col
            return(stacked_table)
        else:
            return(table)
        
        
        
        
    # This aggregate on a series of variables and 
    def aggregate(self, variables_dictionary, aggfunction = np.sum, inplace = False):
        final_column = self.acs_data.columns.to_list()[:2]
        colname = self.colname
        copied_data = self.acs_data.copy()
        for group, sub in variables_dictionary.items():
            for new_name, suffices in sub.items():
                final_column.append(new_name)
                variables = ['(' + group + '_' + x + ')' for x in suffices]
                regex = '|'.join(variables)
                pattern = re.compile(regex, flags = re.I)
                index = colname.str.match(pattern)
                column = colname[index]
                sliced = self.acs_data.copy()
                sliced = sliced.loc[:, column]
                sliced = sliced.astype(float)
                if inplace:
                    self.acs_data[new_name] = sliced.aggregate(func = aggfunction, axis = 1)
                    self.refresh()
                else:
                    copied_data[new_name] = sliced.aggregate(func = aggfunction, axis = 1)
                    copied_data = copied_data.sort_values('FIPS').reset_index( drop = True)
        if inplace:
            return(self.acs_data)
        else:
            return(copied_data.loc[:, final_column])
        
    def iaggregate(self, variables_dictionary, aggfunction = np.sum, inplace = False):
        self.refresh()
        final_column = self.acs_data.columns.to_numpy()[:2]
        colname =self.colname.sort_values()
        copied_data = self.acs_data.copy().sort_values('FIPS').reset_index(drop = True)
        for group, sub in variables_dictionary.items():
            for new_name, suffices in sub.items():
                final_column = np.append(final_column, f'{new_name}_{group}')
                variables = np.array(suffices) - 1
                index = colname.str.match(re.compile(group, flags = re.I))
                column = colname[index]
                column = column[variables]
                sliced = self.acs_data.copy().sort_values('FIPS').reset_index(drop = True)
                sliced = sliced.loc[:, column]
                sliced = sliced.astype(float)
                if inplace:
                    self.acs_data[f'{new_name}_{group}'] = sliced.aggregate(func = aggfunction, axis = 1)
                    self.refresh()
                else:
                    copied_data[f'{new_name}_{group}'] = sliced.aggregate(func = aggfunction, axis = 1)
                    copied_data = copied_data.sort_values('FIPS').reset_index( drop = True)
        if inplace:
            self.refresh()
            return(self.acs_data)
        else:
            return(copied_data.loc[:, final_column])
        
        
        
        
        
    def gen_subgroups(self, new_variables, groups):
        from functools import reduce
        from itertools import product
        self.refresh()
        # First, we need to find the combinations of the new_variables where they contain at least one original variable in the group.
        # For example, the combination of Age under 18 years and No computer in home and broadband access does not have cases because
        # not having a computer excludes the cases where you have the broadband access.
        variables = list(new_variables.keys())
        subgroups = [list(x.keys()) for x in list(new_variables.values())]
        subindex = [list(x.values()) for x in list(new_variables.values())]
        comb_subgroups = np.array(list(product(*subgroups)))
        subgroups_index = list(map(lambda x: reduce(np.intersect1d, x), list(product(*subindex))))
        index_size = np.array(list(map(lambda x: x.shape[0], subgroups_index)))
        comb_subgroups = comb_subgroups[np.not_equal(index_size, 0)]
        subgroups_index = list(map(lambda x : subgroups_index[x], (np.arange(len(subgroups_index))[np.not_equal(index_size, 0)])))
        subgroups_index = [x.tolist() for x in subgroups_index]
        copy = self.acs_data.copy().sort_values('FIPS')
        frame = pd.DataFrame(comb_subgroups, columns = variables)
        n = frame.shape[0]
        p = frame.shape[1]
        N = copy.shape[0]
        frame = pd.concat([frame]*N, ignore_index = True)
        index = np.repeat(copy.FIPS, n)
        frame.index = index
        frame = frame.merge(copy, how = 'left', left_on = 'FIPS', right_on = 'FIPS').iloc[:, [0, p+1, p+2 ] + list(range(1, p+1))]
        comb_subgroups = list(map(lambda x: ' & '.join(x), comb_subgroups))
        arg = dict(zip(comb_subgroups, subgroups_index))
        arg1 = {}
        if type(groups) == str:
            arg1[groups] = arg
        else:
            for i in groups:
                arg1[i]= arg
        self.temp = self.iaggregate(arg1)
        temp = self.temp.iloc[:,2:]
        k = int(temp.shape[1]/n)
        for i in range(int(k)):
            column_index = range(i*n, (i+1)*n)
            source = temp.iloc[:, column_index]
            frame[groups[i]] = source.to_numpy().reshape(-1)
        frame = frame.reset_index(drop = True)
        return(frame)
    
    
    def merge_gen_subgroups(self, list_new_variables, list_groups):
        output = self.gen_subgroups(list_new_variables[0], list_groups[0])
        new_variables = list_new_variables[0]
        # I just need to find n
        variables = list(new_variables.keys())
        n = len(variables)
        for i in range(1, len(list_new_variables)):
            new_output = self.gen_subgroups(list_new_variables[i], list_groups[i])
            output = output.merge(new_output, on = list(output.columns[:3+n]))
        return(output)