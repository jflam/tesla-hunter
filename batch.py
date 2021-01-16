#!/usr/bin/env python

from datetime import date
import teslahunter as t 

print(f"Importing Tesla daily used car listings for {date.today()}")
df = t.get_daily_data()

# Write a pickle file and a csv

df.to_pickle(f"data/{date.today()}.pkl")
df.to_csv(f"data/{date.today()}.csv")
