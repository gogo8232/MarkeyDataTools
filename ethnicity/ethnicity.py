#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 14:25:51 2021

@author: leepark
"""

import sys
sys.path.append('/home/leepark/MarkeyDataTools')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import MarkeyDataTools as mdt
import gen_ind_table as git


class ethnicity():
    def __init__(self):
        git_ = git.gen_ind_table('B03003')
        self.table = git_.gen_df()
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
    e = ethnicity()