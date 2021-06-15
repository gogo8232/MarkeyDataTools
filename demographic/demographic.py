#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 13:19:03 2021

@author: leepark
"""



import sys
sys.path.append('../')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import MarkeyDataTools as mdt
import gen_ind_table as git
import concurrent


with concurrent.futures.ProcessPoolExecutor() as executor:
    total = executor.submit(git.gen_ind_table, 'B01001')
    white = executor.submit(git.gen_ind_table, 'B01001H')
    black = executor.submit(git.gen_ind_table, 'B01001B')
    hispanic = executor.submit(git.gen_ind_table, 'B01001I')
    asian = executor.submit(git.gen_ind_table, 'B01001D')
    native = executor.submit(git.gen_ind_table, 'B01001C')
    pacific = executor.submit(git.gen_ind_table, 'B01001E')
    two = executor.submit(git.gen_ind_table, 'B01001G')
    other = executor.submit(git.gen_ind_table, 'B01001F')



table_total = total.result().gen_df()
table_white = white.result().gen_df()
table_black = black.result().gen_df()
table_hispanic = hispanic.result().gen_df()
table_asian = asian.result().gen_df()
table_native = native.result().gen_df()
table_pacific = pacific.result().gen_df()
table_two = two.result().gen_df()
table_other = other.result().gen_df()



# table_total = git.gen_ind_table('B01001').gen_df()
# table_white = git.gen_ind_table('B01001H').gen_df()
# table_black = git.gen_ind_table('B01001B').gen_df()
# table_hispanic = git.gen_ind_table('B01001I').gen_df()
# table_asian = git.gen_ind_table('B01001D').gen_df()
# table_native = git.gen_ind_table('B01001C').gen_df()
# table_pacific = git.gen_ind_table('B01001E').gen_df()
# table_other = git.gen_ind_table('B01001F').gen_df()





table_total.iloc[:,4:] = table_total.iloc[:,4:].astype(int)
table_white.iloc[:,4:] = table_white.iloc[:,4:].astype(int)
table_black.iloc[:,4:] = table_black.iloc[:,4:].astype(int)
table_hispanic.iloc[:,4:] = table_hispanic.iloc[:,4:].astype(int)
table_asian.iloc[:,4:] = table_asian.iloc[:,4:].astype(int)
table_native.iloc[:,4:] = table_native.iloc[:,4:].astype(int)
table_pacific.iloc[:,4:] = table_pacific.iloc[:,4:].astype(int)
table_two.iloc[:,4:] = table_two.iloc[:,4:].astype(int)
table_other.iloc[:,4:] = table_other.iloc[:,4:].astype(int)






total_missing = table_total.columns.to_series()[[(x not in table_white.columns) for x in table_total.columns]].reset_index(drop = True)
sub_missing = table_white.columns.to_series()[[(x not in table_total.columns) for x in table_white.columns]].reset_index(drop = True)

sub_index = [0, 3, 5, 7, 10, 13, 15, 18, 20, 22, 25, 28, 30]

for i in range(len(sub_index)-1):
    table_total[sub_missing[i]] = table_total[total_missing[sub_index[i]:sub_index[i+1]]].apply(np.sum, axis = 1)
    table_total.drop(total_missing[sub_index[i]:sub_index[i+1]], axis = 1, inplace = True)

col = table_total.columns.to_list()
col = col[:4] + sorted(col[4:])
table_total = table_total[col]
table_white = table_white[col]
table_black = table_black[col]
table_black = table_black[col]
table_hispanic = table_hispanic[col]
table_asian = table_asian[col]
table_native = table_native[col]
table_pacific = table_pacific[col]
table_two = table_two[col]
table_other = table_other[col]


def td(table):
    table = table.drop('State', axis = 1)
    table = table.set_index(['FIPS','Tract','County'])
    return(table)

table_total = td(table_total)
table_white = td(table_white)
table_black = td(table_black)
table_hispanic = td(table_hispanic)
table_asian = td(table_asian)
table_native = td(table_native)
table_pacific = td(table_pacific)
table_two = td(table_two)
table_other = td(table_other)


def merge1(left, right, suffix, right_suffix = None):
    if right_suffix == None:
        table = left.merge(right, how = 'left', left_index = True,
                           right_index = True, suffixes = ('',f'_{suffix}'))
    else:
        table = left.merge(right, how = 'left', left_index = True,
                   right_index = True, suffixes = (f'_{right_suffix}',f'_{suffix}'))
    return(table)

tables = [table_white, table_black, table_hispanic, table_asian, table_native, 
          table_pacific, table_two, table_other]

suffices = ['white','black','hispanic','asian','native','pacific','two or more','other']

combined = table_total

for s, t in zip(suffices, tables):
    if s != 'other':
        combined = merge1(combined, t, s)
    else:
        combined = merge1(combined, t, s, right_suffix = 'total')



combined = combined.stack()
combined = combined.reset_index()
combined.columns = combined.columns.to_list()[:3] + ['names', 'count']


combined[['sex','age','race']] = combined.names.str.split('_', expand = True)
combined.dropna(inplace = True)
combined.drop('names',axis = 1, inplace = True)
combined = combined[['FIPS', 'Tract', 'County',  'sex', 'age', 'race','count']]


county_combined = combined.groupby(['County','sex','age','race'], as_index = False).agg(np.sum)










# combined = table_total.merge(table_white, how = 'left', left_index = True, right_index = True,
#                              suffixes = ('', '_white')).merge(table_black, how = 'left',
#                                                                     left_index = True, right_index = True,
#                                                                     suffixes = ('_total','_black'))


# combined_county = combined.groupby('County').agg(np.sum)


