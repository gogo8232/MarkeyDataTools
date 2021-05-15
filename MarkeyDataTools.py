import pandas as pd
import requests
import re
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_colwidth', 0)

class MarkeyDataTools:
    def __init__(self):
        self.key = 'ba1c94e9a1b43440cf3ef2bf0b7803ddc39bcf2d'
        self.census_available_region = np.array(['state','county','county subdivision','tract'])

        
    def find_census_region(self, search_value):
        pattern = re.compile(f'{search_value}$', flags = re.I)
        index = list(map(lambda x: bool(re.search(pattern, x)), self.census_available_region))
        return(self.census_available_region[index][0])
        
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
        
        
class acs(MarkeyDataTools):
    def __init__(self, year, table, source = 'acs5', state = 'KY', region = 'County'):
    # Run the init function of the parent class first
        super().__init__()

    # assign values to the following attributes
        self.year = year
        available_region = ['state','county','county subdivision']
        
        
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
            table = ','.join(list(map(self.find_variable_list, table)))
    # For some reason, it sometimes generate multiple ,'s at the end
    # This should be substituted with a blank.
        pattern = re.compile(',,+')
        table = re.sub(pattern, '', table)   
        self.table = table


    # If the state is Kentucky, the FIPS code 21;
    # Otherwise, it is not going to run
        if state == 'KY':
            self.state = 21
        else:
            print('for now, it works only for the state of Kentucky')


    # cleaning region
        self.region = self.find_census_region(region)

    # generate the variable table
        self.gen_variable_table()





    def __repr__(self):
        message = 'This module is to pull and search the American Community Survey Data; for more information, please visit https://github.com/gogo8232/MarkeyDataTools'      
        return(message)

    # This generates the variable table for the source of the data
    def gen_variable_table(self):
        response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}/variables')
        lists = response.json()
        header, values = lists[0], lists[1:]
        self.variable_table =  pd.DataFrame(values, columns = header)

    # From the variable table, this function allows you to find relevant variables from the 'table' argument you set up.
    def find_variable_list(self, var_name):
        pattern = re.compile(f'{var_name}.*')
        sub_variables = self.variable_table.loc[self.variable_table.name.str.match(pattern),:]
        names = sub_variables.name
        var_name = ','.join(names)
        return(var_name)

    # This generates the data frame using the arguments
    def gen_dataframe(self):
        if self.region == 'state':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get={self.table}&for=state:{self.state}&key={self.key}')
        elif self.region == 'county':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get=NAME,{self.table}&for=county:*&in=state:{self.state}&key={self.key}')
        elif self.region == 'county subdivision':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get=NAME,{self.table}&for=county%20subdivision:*&in=state:{self.state}&in=county:*&key={self.key}')
        elif self.region == 'tract':
            response = requests.get(f'https://api.census.gov/data/{self.year}/{self.source}?get=NAME,{self.table}&for=tract:*&in=state:{self.state}&in=county:*&key={self.key}')
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

        self.acs_data = df
        return(self.acs_data)
    
    def search(self, keyword, savefile = False, filename = ''):
        try:
            self.groups
        except:
            self.get_acs_groups(self.year)
        df = self.groups
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

            