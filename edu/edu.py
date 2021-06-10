import sys
sys.path.append('/home/leepark/MarkeyDataTools')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import MarkeyDataTools as mdt
import gen_ind_table as git


class edu:
    def __init__(self):
        git_ = git.gen_ind_table('B15003')
        df = git_.gen_df()
        col1 = ['Nursery school', 'No schooling completed', '5th grade', '3rd grade', '4th grade', '2nd grade', '1st grade', 'Kindergarten','8th grade', '7th grade', '6th grade']
        col2 = ['11th grade', '10th grade', '9th grade', 'GED or alternative credential', 'Regular high school diploma', '12th grade, no diploma']
        col3 = ["Bachelor's degree", "Associate's degree", "Some college, 1 or more years, no degree",'Some college, less than 1 year']
        col4 = ['Doctorate degree','Professional school degree', "Master's degree"]
        df['below 9th grade'] = df.loc[:, col1].apply(np.sum, axis =1)
        df.drop(col1, axis = 1, inplace = True)
        df['some highschool'] = df.loc[:, col2].apply(np.sum, axis =1)
        df.drop(col2, axis = 1, inplace = True)
        df['some college'] = df.loc[:, col3].apply(np.sum, axis = 1)
        df.drop(col3, axis = 1, inplace = True)
        df['advanced degree'] = df.loc[:, col4].apply(np.sum, axis = 1)
        df.drop(col4, axis = 1, inplace = True)
        df = df[['FIPS', 'Tract', 'County', 'State', 'below 9th grade', 'some highschool',
                 'some college', 'advanced degree', 'total']]
        self.table = df
        self.region = 'tract'
        self.total = git_.gen_total()
        self.table['total'] = self.total.total.astype(float)
        self.table.iloc[:, 4:] = self.table.iloc[:, 4:].astype(float)
    
    def define_region(self, region = 'tract', return_table = True):
        self.region = region.lower()
        if region.lower() == 'tract':
            if return_table:
                return(self.table)
        elif region.lower() == 'county':
            if return_table:
                return(self.table.groupby(['State','County']).agg(np.sum))
            self.county_level_data_raw = self.table.groupby(['State','County']).agg(np.sum).reset_index()
        else:
            print('It only supports that tract or county level data')
    
    def percentage(self):
        try:
            self.region
        except:
            self.define_region('tract')
        self.perc = True

        if self.region == 'tract':
            self.table_perc = self.table.set_index(['FIPS', 'Tract','County','State']).apply(lambda x: x/(x.total+.000001), axis = 1).drop('total', axis = 1).reset_index()
            return(self.table.set_index(['FIPS', 'Tract','County','State']).apply(lambda x: x/(x.total+.0001), axis = 1).drop('total', axis = 1).reset_index())
        else:
            self.county_level_data_perc = self.table.groupby(['State','County']).agg(sum).apply(lambda x: x/x.total, axis = 1).drop('total', axis = 1).reset_index()
            return(self.county_level_data_perc)
    
    def tract(self, tract_name, perc = False):
        pattern = re.compile(f'.*{tract_name}.*')
        if perc:
            try:
                self.table_perc
            except:
                self.region = 'tract'
                _ = self.percentage()
            n = len(self.table_perc.loc[self.table_perc.Tract.str.match(pattern),:])
            if n > 0:
                return(self.table_perc.loc[self.table_perc.Tract.str.match(pattern),:])
            else:
                return(self.table_perc.loc[self.table_perc.County.str.match(pattern),:])
        else:
            n = len(self.table.loc[self.table.Tract.str.match(pattern),:])
            if n > 0:
                return(self.table.loc[self.table.Tract.str.match(pattern),:])
            else:
                return(self.table.loc[self.table.County.str.match(pattern), :])
            
    def county(self, county_name, perc = False):
        pattern = re.compile(f'.*{county_name}.*')
        self.region = 'county'
        if perc:
            _ = self.percentage()
            return(self.county_level_data_perc.loc[self.county_level_data_perc.County.str.match(pattern),:])
        else:
            self.define_region(region = 'county', return_table = False)
            return(self.county_level_data_raw.loc[self.county_level_data_raw.County.str.match(pattern), :])



if __name__ == '__main__':
    e = edu()