#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 14:09:23 2021

@author: leepark
"""


import sys
sys.path.append('./*/')
sys.path.append('./')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import MarkeyDataTools as mdt
import gen_ind_table as git
from aged.aged import aged
from edu.edu import edu
from employment.employment import employment
from ethnicity.ethnicity import ethnicity
from housing.rent_to_income import rent_to_income
from housing.tenure import tenure
from housing.vacancy import vacancy
from housing.years import years
from income.income import income
from income.poverty import poverty
from insurance.insurance import insurance
from nativity.nativity import nativity
from origin.origin import origin
from transportation.means import means
from transportation.travel import travel


variables = [aged, edu, employment, ethnicity, rent_to_income, tenure, vacancy,
             years, income, poverty, insurance, nativity, origin, means, travel]

variable_names = ['age', 'education', 'employment', 'ethnicity','rent_to_income', 
                  'tenure', 'vacancy', 'years', 'income', 'poverty', 'insurance', 
                  'nativity', 'origin', 'means', 'travel']

var_dict = dict(zip(variable_names, variables))


def tract_level_raw():
    print(list(var_dict.keys()))
    var = str(input('type a variable to look up from above : ' ))
    _class = var_dict[var]()
    table = _class.table
    return(table)


def tract_level_perc():
    print(list(var_dict.keys()))
    var = str(input('type a variable to look up from above : ' ))
    _class = var_dict[var]()
    table = _class.percentage()
    return(table)


def county_level_raw():
    print(list(var_dict.keys()))
    var = str(input('type a variable to look up from above : ' ))
    _class = var_dict[var]()
    table = _class.define_region('county')
    table.reset_index(inplace = True)
    return(table)


def county_level_perc():
    print(list(var_dict.keys()))
    var = str(input('type a variable to look up from above : ' ))
    _class = var_dict[var]()
    _class.define_region('county', return_table = False)
    table = _class.percentage()
    return(table)






# age = aged()
# edu = edu()
# employment = employment()
# ethnicity = ethnicity()
# rent_to_income = rent_to_income()
# tenure = tenure()
# vacancy = vacancy()
# years = years()
# income = income()
# poverty = poverty()
# insurance= insurance()
# nativity = nativity()
# origin = origin()
# means = means()
# travel = travel()
