# Script for querying Tesla Inventory REST API
# This reddit post is an excellent resource for
# how to hack this API:
# 
# https://www.reddit.com/r/TeslaLounge/comments/jwu5z0/having_fun_with_the_used_inventory_api_and_price/

#%%
INVENTORY_API = "https://www.tesla.com/inventory/api/v1/inventory-results?query="

from io import StringIO
import json
from IPython.core.display import HTML 
import requests
import urllib

# This is a sample JSON query object that is sent to the API
#
# {
#   "query":
#   {
#     "model":"m3",
#     "condition":"used",
#     "options":{
#       "TRIM":["MRRWD","LRRWD","LRAWD"],
#       "AUTOPILOT":["AUTOPILOT_FULL_SELF_DRIVING"]
#     },
#     "arrangeby":"Price",
#     "order":"asc",
#     "market":"US",
#     "language":"en",
#     "super_region":"north america",
#     "lng":-122.1257,
#     "lat":47.6722,
#     "zip":"98052",
#     "range":0
#   },
#   "offset":0,
#   "count":50,
#   "outsideOffset":0,
#   "outsideSearch":false
# }

SAMPLE_QUERYPARAMS = '{"query":{"model":"m3","condition":"used","options":{"TRIM":["MRRWD","LRRWD","LRAWD"],"AUTOPILOT":["AUTOPILOT_FULL_SELF_DRIVING"]},"arrangeby":"Price","order":"asc","market":"US","language":"en","super_region":"north america","lng":-122.1257,"lat":47.6722,"zip":"98052","range":0},"offset":0,"count":50,"outsideOffset":0,"outsideSearch":false}'

# Let's do the simplest possible thing and send that QUERYPARAM as 
# a URLENCODED string appended to the INVENTORY_API call and print
# the result


#%%
QUERY=urllib.parse.quote(SAMPLE_QUERYPARAMS)

# Now let's make the request to the actual API and look at the results

r = requests.get(INVENTORY_API+QUERY)
# %%

# Let's make it easier to run things by representing QUERYPARAMS as a Python object

obj = {
    "query": {
        "model": "m3",
        "condition": "used",
        "options": {
            # MRRWD|LRRWD|SRPRWD|LRAWD
            "TRIM": ["LRAWD"],
            # WHITE|RED|BLACK|SILVER
            # "PAINT": ["WHITE","GRAY"],
            # EIGHTEEN|NINETEEN
            # "WHEELS": ["NINETEEN"],
            "AUTOPILOT": ["AUTOPILOT_FULL_SELF_DRIVING"],
            # PREMIUM_BLACK|PREMIUM_WHITE
            "INTERIOR": ["PREMIUM_WHITE"]
        },
        "arrangeby": "Price",
        "order": "asc",
        "market": "US",
        "language": "en",
        "region": "north america"
        # "super_region": "north america",
        # "lng": -122.1257,
        # "lat": 47.6722,
        # "zip": "98052",
        # "range": 1000 
    },
    # "offset": 0,
    # # "count": 5000,
    # "outsideOffset": 0,
    # "outsideSearch": "false"
}

# Take the object
# Turn it into a JSON string
# UrlEncode it
# Send it to the Tesla Inventory API

str=json.dumps(obj)
urlstr=urllib.parse.quote(str)
r2 = requests.get(INVENTORY_API+urlstr)

# Parse the return object as json

results = r2.json()

# So the return value results is
# a dict that contains a value called "results"
# number of values returned is in a peer entry called "total_matches_found"

# So let's start by printing out the total matches found

print(f"there are {len(results['results'])} cars in this page")
print(f"there are {results['total_matches_found']} total records in result set")

#%%

# Let's define types for everything

import enum 
from datetime import datetime
from typing import List, Tuple

class ExteriorColor(enum.Enum):
    RED = 'Red Multi-Coat'
    WHITE = 'Pearl White Multi-Coat'
    SILVER = 'Silver Metallic'
    BLUE = 'Deep Blue Metallic'
    BLACK = 'Solid Black'
    GRAY = 'Midnight Silver Metallic'
    UNKNOWN = 'UNKNOWN'

class InteriorColor(enum.Enum):
    BLACK = 'PREMIUM_BLACK'
    WHITE = 'PREMIUM_WHITE'
    UNKNOWN = "UNKNOWN"

class Drivetrain(enum.Enum):
    LRAWD = "Long Range AWD"
    LRAWDP = "Long Range AWD Performance"
    LRRWD = "Long Range RWD"
    MRRWD = "Medium Range RWD"
    SRPRWD = "Standard Range Plus RWD"
    UNKNOWN = "UNKNOWN"

class Wheels(enum.Enum):
    EIGHTEEN = '18" Aero Wheels'
    NINETEEN = '19" Sport Wheels'
    TWENTY = '20" Fragile Wheels'
    UNKNOWN = "UNKNOWN"

class Car:
    VIN : str
    ExteriorColor : ExteriorColor
    InteriorColor : InteriorColor 
    Wheels : str 
    Mileage : int 
    Drivetrain : Drivetrain 
    AccelerationBoost : bool 
    OriginalDeliveryDate : str  # todo: datetime 
    History : str 
    PhotoUris : List[str]
    Price : int
    PriceHistory : List[int]
    ModelYear : int
    Location : str
    Price : int

    def __init__(self, 
                 vin : str, 
                 exterior_color : ExteriorColor, 
                 interior_color : InteriorColor,
                 drivetrain : Drivetrain,
                 wheels : str,
                 mileage : int,
                 photos : List[str],
                 year : int,
                 location : str,
                 price : int):

        self.VIN = vin 
        self.ExteriorColor = exterior_color
        self.InteriorColor = interior_color
        self.Drivetrain = drivetrain
        self.Wheels = wheels
        self.Mileage = mileage
        self.PhotoUris = photos
        self.ModelYear = year
        self.Location = location
        self.Price = price

    def get_tesla_details_page_uri(self):
        return f"https://www.tesla.com/used/{self.VIN}"

class Price:
    Prices : List[Tuple[int, datetime]]
    
    def get_current(self) -> Tuple[int, datetime]:
        if self.Prices.count == 0:
            return None 
        else: 
            return self.Prices[self.Prices.count -1]
    
    def add(self, price : int, dt, datetime) -> None:
        self.Prices.append((price, dt))

#%%

# Helper functions

def exterior_color(car) -> ExteriorColor:
    paint=car["PAINT"][0]
    if paint == "BLUE":
        return ExteriorColor.BLUE
    elif paint == "RED":
        return ExteriorColor.RED
    elif paint == "WHITE":
        return ExteriorColor.WHITE
    elif paint == "BLACK":
        return ExteriorColor.BLACK
    elif paint == "SILVER":
        return ExteriorColor.SILVER
    elif paint == "GRAY":
        return ExteriorColor.GRAY
    else:
        print(f"unknown color: {paint}")
        return ExteriorColor.UNKNOWN

def interior_color(car) -> InteriorColor:
    color=car["INTERIOR"][0]
    if color == "PREMIUM_BLACK":
        return InteriorColor.BLACK
    elif color == "PREMIUM_WHITE":
        return InteriorColor.WHITE
    else:
        print(f"unknown interior color: {color}")
        return InteriorColor.UNKNOWN

def get_drivetrain(car) -> Drivetrain:
    drive=car["TRIM"][0]
    if drive == "LRAWD":
        return Drivetrain.LRAWD
    elif drive == "LRAWDP":
        return Drivetrain.LRAWDP
    elif drive == "MRRWD":
        return Drivetrain.MRRWD
    elif drive == "LRRWD":
        return Drivetrain.LRRWD
    elif drive == "SRPRWD":
        return Drivetrain.SRPRWD
    else:
        print(f"unknown drivetrain: {drive}")
        return Drivetrain.UNKNOWN

def get_wheels(car) -> Wheels:
    size=car["WHEELS"][0]
    if size == "EIGHTEEN":
        return Wheels.EIGHTEEN
    elif size == "NINETEEN":
        return Wheels.NINETEEN
    elif size == "TWENTY":
        return Wheels.TWENTY
    else:
        print(f"unknown wheelsize: {size}")
        return Wheels.UNKNOWN

def get_pictures(car) -> List[str]:
    photos=car["VehiclePhotos"]
    uris=[]
    for photo in photos:
        uris.append(photo["imageUrl"])
    return uris

from IPython.display import display, Image 
import requests

def display_picture(uri):
    try:
        img=requests.get(uri).content
        display(Image(img))
    except:
        display("unauthorized")

# %%

# Iterate over results vector

cars=results["results"]
objs=[]
for car in cars:
    vin=car["VIN"]
    price=car["Price"]
    is_demo=car["IsDemoVehicle"]
    location=car["MetroName"]
    mileage=car["Odometer"]
    year=car["Year"]
    c = Car(vin, 
            exterior_color(car), 
            interior_color(car), 
            get_drivetrain(car), 
            get_wheels(car), 
            mileage, 
            get_pictures(car),
            year,
            location,
            price)
    objs.append(c)
    print(f"{c.Price} {c.ModelYear} {c.ExteriorColor.value} {c.Mileage} miles in {c.Location} {c.VIN}")
# %%

# Function that generates a bunch of links to cars

from IPython.display import display, HTML
def generate_links(cars):
    html='<table>'
    for car in cars:
        html += '<tr>'
        html += f'<td>${format(car.Price, ",d")}</td>'
        html += f'<td>{car.ModelYear}</td>'
        html += f'<td style="text-align:left">{car.Drivetrain.value}</td>'
        html += f'<td style="text-align:left">{car.ExteriorColor.value}</td>'
        html += f'<td style="text-align:left">{car.Wheels.value}</td>'
        html += f'<td>{format(car.Mileage, ",d")}</td>'
        html += f'<td>{car.Location}</td>'
        html += f'<td><a href="{car.get_tesla_details_page_uri()}">{car.VIN}</a></td>'
        html += f'<td><a href="https://www.teslacpo.io/vin/{car.VIN}">history</a></td>'
        html += '</tr>'
    html += "</table>"
    display(HTML(html))
    
#%%

import pandas as pd 

# Function that takes the vector of car objects and converts to a pandas dataframe

def to_dataframe(cars) -> pd.DataFrame:
    df = pd.DataFrame(columns=['VIN', 'Price', 'Year', 'Exterior Color', 'Wheels', 'Mileage', 'Location'])
    i = 0
    for car in cars:
        df.loc[i] = [car.VIN, car.Price, car.ModelYear, car.ExteriorColor.value, car.Wheels.value, car.Mileage, car.Location]
        i += 1
    return df.set_index(["VIN"])

#%%

df=to_dataframe(objs)
# %%

query = {
    "query": {
        "model": "m3",
        "condition": "used",
        "options": {
            # MRRWD|LRRWD|SRPRWD|LRAWD
            # "TRIM": ["LRAWD"],
            # WHITE|RED|BLACK|SILVER
            # "PAINT": ["WHITE","GRAY"],
            # EIGHTEEN|NINETEEN
            # "WHEELS": ["NINETEEN"],
            # "AUTOPILOT": ["AUTOPILOT_FULL_SELF_DRIVING"],
            # PREMIUM_BLACK|PREMIUM_WHITE
            # "INTERIOR": ["PREMIUM_WHITE"]
        },
        "arrangeby": "Price",
        "order": "asc",
        "market": "US",
        "language": "en",
        "region": "north america"
    },
}

# Function to retrieve a page of results from tesla inventory API

def query_tesla(query):
    cars=[]
    offset=0

    def query_page(query, offset):
        query["outsideOffset"]=offset
        query_str=json.dumps(query)
        url_str=urllib.parse.quote(query_str)
        r=requests.get(INVENTORY_API+url_str)
        return r.json()

    while True:
        r=query_page(query, offset)

        results=r["results"]
        for result in results:
            vin=result["VIN"]
            price=result["Price"]
            is_demo=result["IsDemoVehicle"]
            location=result.get("MetroName", None)
            mileage=result["Odometer"]
            year=result["Year"]
            car = Car(vin, 
                      exterior_color(result), 
                      interior_color(result), 
                      get_drivetrain(result), 
                      get_wheels(result), 
                      mileage, 
                      get_pictures(result),
                      year,
                      location,
                      price)
            cars.append(car)

        if offset+len(r["results"]) >= int(r["total_matches_found"]):
            break

        offset+=len(r["results"])
    
    return cars

cars=query_tesla(query)
# %%

# Fun with enums

import teslatypes as tt 

