#%%

import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib as plt

from climate_data import *

city_folders = ['chicago', 'manitowoc', 'milwaukee', 'ludington']

df = load_data(city_folders)



