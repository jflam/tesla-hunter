import enum, json, requests, urllib
import pandas as pd 
from datetime import datetime
from typing import List, Tuple

INVENTORY_API = "https://www.tesla.com/inventory/api/v1/inventory-results?query="

class ExteriorColor(enum.Enum):
    RED = 'Red Multi-Coat'
    WHITE = 'Pearl White Multi-Coat'
    SILVER = 'Silver Metallic'
    BLUE = 'Deep Blue Metallic'
    BLACK = 'Solid Black'
    GRAY = 'Midnight Silver Metallic'
    UNKNOWN = 'Unknown Exterior Color'

class InteriorColor(enum.Enum):
    PREMIUM_BLACK = 'Premium Black'
    PREMIUM_WHITE = 'Premium Black and White'
    UNKNOWN = 'Unknown Interior Color'

class Drivetrain(enum.Enum):
    LRAWD = 'Long Range AWD'
    LRAWDP = 'Long Range AWD Performance'
    LRRWD = 'Long Range RWD'
    MRRWD = 'Medium Range RWD'
    SRPRWD = 'Standard Range Plus RWD'
    UNKNOWN = 'Unknown Drivetrain'

class Wheels(enum.Enum):
    EIGHTEEN = '18" Aero Wheels'
    NINETEEN = '19" Sport Wheels'
    TWENTY = '20" Fragile Wheels'
    UNKNOWN = "Unknown Wheel Type"

# Return descriptions for UX

def get_descriptions(t : enum.Enum):
    return [v.value for v in t]

# Lookup an Enum value based on the description

def get_value(t : enum.Enum, description : str):
    for e in t:
        if e.name == description:
            return e
    # Also print out the unknown description
    print(f"Unknown {description} while looking up {t}")
    return t.UNKNOWN # this is by convention

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

def create_query(drivetrains, exterior_colors, interior_colors, wheels):
    def to_str_list(l : List) -> List[str]:
        [e.name for e in l]

    query = {
        "query": {
            "model": "m3",
            "condition": "used",
            "options": {
                "TRIM": to_str_list(drivetrains),
                "PAINT": to_str_list(exterior_colors),
                "INTERIOR": to_str_list(interior_colors),
                "WHEELS": to_str_list(wheels)
            },
            "arrangeby": "Price",
            "order": "asc",
            "market": "US",
            "language": "en",
            "region": "north america"
        },
    }
    return query

# Helper functions

# def exterior_color(car) -> ExteriorColor:
#     paint=car["PAINT"][0]
#     if paint == "BLUE":
#         return ExteriorColor.BLUE
#     elif paint == "RED":
#         return ExteriorColor.RED
#     elif paint == "WHITE":
#         return ExteriorColor.WHITE
#     elif paint == "BLACK":
#         return ExteriorColor.BLACK
#     elif paint == "SILVER":
#         return ExteriorColor.SILVER
#     elif paint == "GRAY":
#         return ExteriorColor.GRAY
#     else:
#         print(f"unknown color: {paint}")
#         return ExteriorColor.UNKNOWN

# def interior_color(car) -> InteriorColor:
#     color=car["INTERIOR"][0]
#     if color == "PREMIUM_BLACK":
#         return InteriorColor.BLACK
#     elif color == "PREMIUM_WHITE":
#         return InteriorColor.WHITE
#     else:
#         print(f"unknown interior color: {color}")
#         return InteriorColor.UNKNOWN

# def get_drivetrain(car) -> Drivetrain:
#     drive=car["TRIM"][0]
#     if drive == "LRAWD":
#         return Drivetrain.LRAWD
#     elif drive == "LRAWDP":
#         return Drivetrain.LRAWDP
#     elif drive == "MRRWD":
#         return Drivetrain.MRRWD
#     elif drive == "LRRWD":
#         return Drivetrain.LRRWD
#     elif drive == "SRPRWD":
#         return Drivetrain.SRPRWD
#     else:
#         print(f"unknown drivetrain: {drive}")
#         return Drivetrain.UNKNOWN

# def get_wheels(car) -> Wheels:
#     size=car["WHEELS"][0]
#     if size == "EIGHTEEN":
#         return Wheels.EIGHTEEN
#     elif size == "NINETEEN":
#         return Wheels.NINETEEN
#     elif size == "TWENTY":
#         return Wheels.TWENTY
#     else:
#         print(f"unknown wheelsize: {size}")
#         return Wheels.UNKNOWN

def get_pictures(car) -> List[str]:
    photos=car["VehiclePhotos"]
    uris=[]
    for photo in photos:
        uris.append(photo["imageUrl"])
    return uris

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
                      get_value(ExteriorColor, result["PAINT"][0]),
                      get_value(InteriorColor, result["INTERIOR"][0]),
                      get_value(Drivetrain, result["TRIM"][0]),
                      get_value(Wheels, result["WHEELS"][0]),
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

# Function that takes the vector of car objects and converts to a pandas dataframe

def to_dataframe(cars) -> pd.DataFrame:
    df = pd.DataFrame(columns=['VIN', 'Price', 'Year', 'Exterior Color', 'Wheels', 'Mileage', 'Location'])
    i = 0
    for car in cars:
        df.loc[i] = [car.VIN, car.Price, car.ModelYear, car.ExteriorColor.value, car.Wheels.value, car.Mileage, car.Location]
        i += 1
    return df.set_index(["VIN"])