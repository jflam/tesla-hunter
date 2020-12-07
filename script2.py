# Another take on the code, partially refactored into teslahunter.py

# %%
import teslahunter as tt

#%%

import importlib 
importlib.reload(tt)

drivetrains = [tt.Drivetrain.LRAWD]
exterior_colors = [tt.ExteriorColor.WHITE]
interior_colors = [tt.InteriorColor.PREMIUM_BLACK]
wheels = [tt.Wheels.EIGHTEEN]

query = tt.create_query(drivetrains, exterior_colors, interior_colors, wheels)
cars = tt.query_tesla(query)
df = tt.to_dataframe(cars)
df

# %%
from datetime import date
print(date.today())
# %%

import time 
import teslahunter as t 

#%%
import importlib 
importlib.reload(t)
t.get_daily_data()

# %%
import pandas as pd
df = pd.read_pickle(f"{date.today()}.pkl")
rm = df.sample(5)
df.drop(rm.index)
# %%
# TODO: this reload functionality really needs to be part of the tool, perhaps as an option?
importlib.reload(t)

df = pd.read_pickle("2020-11-25.pkl")
days = t.synthesize_data(df)

# %%

df = pd.read_pickle("2020-11-25.pkl")

days = 10
add_per_day = 10
sold_per_day = 5
price_adjustment = 350

dfs = [df]
current_df = df
for _ in range(days):
    rows = len(current_df.index)
    new_df = current_df.sample(frac=((rows - add_per_day)/rows))
    new_df['Price'] = new_df['Price'] - price_adjustment
    dfs.insert(0, new_df)
    current_df = new_df

for df in dfs:
    print(len(df.index))

# Simulate selling 5 cars per day
# For each day, sample 5 cars to remove and add them to cars to remove list
# Remove them from that day's list
# Sample 5 more cars, add them to the remove list and remove 10 cars 
# Repeat

sold_list = dfs[0].sample(sold_per_day).index.tolist()
for i in range(1, len(dfs)):
    dfs[i] = dfs[i].drop(sold_list)
    newly_sold = dfs[i].sample(sold_per_day).index.tolist()
    sold_list += newly_sold

for df in dfs:
    print(len(df.index))
# %%

# %%
