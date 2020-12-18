# teslahunter - a library for querying the Tesla Used inventory API

import enum, json, requests, urllib, time, pickle
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Union
from datetime import date
from os import path


INVENTORY_API = "https://www.tesla.com/inventory/api/v1/inventory-results?query="


class Model(enum.Enum):
    M3 = "Model 3"
    MS = "Model S"
    MX = "Model X"
    MY = "Model Y"
    UNKNOWN = "Unknown Model"


class ExteriorColor(enum.Enum):
    RED = "Red Multi-Coat"
    WHITE = "Pearl White Multi-Coat"
    SILVER = "Silver Metallic"
    BLUE = "Deep Blue Metallic"
    BLACK = "Solid Black"
    GRAY = "Midnight Silver Metallic"
    GREY = "Model X Grey"
    BROWN = "Brown Metallic"
    UNKNOWN = "Unknown Exterior Color"


class InteriorColor(enum.Enum):
    PREMIUM_BLACK = "Premium Black"
    PREMIUM_WHITE = "Premium Black and White"
    TAN = "Tan"
    CREAM = "Cream Premium"
    WHITE = "White"
    BLACK = "Black"
    GREY = "Grey"
    BLACK_TEXTILE = "Black Cloth"
    UNKNOWN = "Unknown Interior Color"


class Drivetrain(enum.Enum):
    # M3
    LRAWD = "Long Range AWD"
    LRAWDP = "Long Range AWD Performance"
    LRRWD = "Long Range RWD"
    MRRWD = "Medium Range RWD"
    SRPRWD = "Standard Range Plus RWD"
    # MS/MX
    _60 = "60Kwh"
    _70 = "70Kwh"
    _75 = "75Kwh"
    _85 = "85Kwh"
    _70D = "Dual Motor 70Kwh"
    _75D = "Dual Motor 75Kwh"
    _85D = "Dual Motor 85Kwh"
    _90D = "Dual Motor 90Kwh"
    _100DE = "Dual Motor 100Kwh"
    P85 = "85Kwh Performance"
    P85D = "Dual Motor 85Kwh Performance"
    P85DL = "Dual Motor 85Kwh Ludicrous"
    P90D = "Dual Motor 90Kwh Performance"
    P90DL = "Dual Motor 90Kwh Ludicrous"
    P100D = "Dual Motor 100Kwh Performance"
    P100DL = "Dual Motor 100Kwh Ludicrous"
    LRPLUS = "Long Range Plus AWD"
    UNKNOWN = "Unknown Drivetrain"


class Wheels(enum.Enum):
    EIGHTEEN = '18" Aero Wheels'
    NINETEEN = '19" Sport Wheels'
    TWENTY = '20" Fragile Wheels'
    TWENTY_ONE = '21" Wheels'
    TWENTY_TWO = '22" Wheels'
    UNKNOWN = "Unknown Wheel Type"


# Return descriptions for UX


def get_descriptions(t: enum.Enum):
    return [v.value for v in t]


# Lookup an Enum value based on the description


def get_value(t: enum.Enum, description: str):
    for e in t:
        if e.value == description:
            return e
    # Also print out the unknown description
    print(f"Unknown {description} while looking up {t}")
    return t.UNKNOWN  # this is by convention


# Lookup an Enum value based on the code in results


def lookup_code(t: enum.Enum, code: str):
    # If code starts with a number, prefix code with an _
    if code[0].isdigit():
        code = "_" + code

    for e in t:
        if e.name == code:
            return e
    # Also print out the unknown description
    print(f"Unknown {code} while looking up {t}")
    return t.UNKNOWN  # this is by convention


class Car:
    VIN: str
    ExteriorColor: ExteriorColor
    InteriorColor: InteriorColor
    Wheels: str
    Mileage: int
    Drivetrain: Drivetrain
    AccelerationBoost: bool
    OriginalDeliveryDate: str  # todo: datetime
    History: str
    PhotoUris: List[str]
    Price: int
    PriceHistory: List[int]
    ModelYear: int
    Location: str
    Price: int
    VehicleHistory: str
    Model: Model

    def __init__(
        self,
        vin: str,
        exterior_color: ExteriorColor,
        interior_color: InteriorColor,
        drivetrain: Drivetrain,
        wheels: str,
        mileage: int,
        photos: List[str],
        year: int,
        location: str,
        price: int,
        vehicle_history: str,
        model: Model,
    ):

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
        self.VehicleHistory = vehicle_history
        self.Model = model

    def get_tesla_details_page_uri(self):
        return f"https://www.tesla.com/used/{self.VIN}"


class Price:
    Prices: List[Tuple[int, datetime]]

    def get_current(self) -> Tuple[int, datetime]:
        if self.Prices.count == 0:
            return None
        else:
            return self.Prices[self.Prices.count - 1]

    def add(self, price: int, dt, datetime) -> None:
        self.Prices.append((price, dt))


# This is the public entry point


def query(model, drivetrains, exterior_colors, interior_colors, wheels):
    query = create_query(model, drivetrains, exterior_colors, interior_colors, wheels)
    return query_tesla(query, model)


def create_query(model, drivetrains, exterior_colors, interior_colors, wheels):
    def to_str_list(l: List) -> List[str]:
        return [e.name for e in l]

    query = {
        "query": {
            "condition": "used",
            "arrangeby": "Price",
            "order": "asc",
            "market": "US",
            "language": "en",
            "region": "north america",
        },
    }

    query["query"]["model"] = model.name.lower()

    # programmatically build options based on presence of options (none means no filter)

    trim = to_str_list(drivetrains)
    paint = to_str_list(exterior_colors)
    interior = to_str_list(interior_colors)
    whls = to_str_list(wheels)

    options = {}
    if len(trim) > 0:
        options["TRIM"] = trim
    if len(paint) > 0:
        options["PAINT"] = paint
    if len(interior) > 0:
        options["INTERIOR"] = interior
    if len(whls) > 0:
        options["WHEELS"] = whls
    query["query"]["options"] = options

    print(query)
    return query


def get_pictures(car) -> List[str]:
    photos = car["VehiclePhotos"]
    uris = []
    for photo in photos:
        uris.append(photo["imageUrl"])
    return uris


# Function to retrieve a page of results from tesla inventory API


def query_tesla(query, model: Model) -> List[Car]:
    cars = []
    offset = 0

    def query_page(query, offset):
        query["outsideOffset"] = offset
        query_str = json.dumps(query)
        url_str = urllib.parse.quote(query_str)
        r = requests.get(INVENTORY_API + url_str)
        return r.json()

    while True:
        r = query_page(query, offset)

        results = r["results"]
        for result in results:
            vin = result["VIN"]
            price = result["Price"]
            location = result.get("MetroName", None)
            mileage = result["Odometer"]
            year = result["Year"]
            vehicle_history = result["VehicleHistory"]
            car = Car(
                vin,
                lookup_code(ExteriorColor, result["PAINT"][0]),
                lookup_code(InteriorColor, result["INTERIOR"][0]),
                lookup_code(Drivetrain, result["TRIM"][0]),
                lookup_code(Wheels, result["WHEELS"][0]),
                mileage,
                get_pictures(result),
                year,
                location,
                price,
                vehicle_history,
                model,
            )
            cars.append(car)

        if offset + len(r["results"]) >= int(r["total_matches_found"]):
            break

        offset += len(r["results"])

    return cars


# Function that takes the vector of car objects and converts to a pandas dataframe


def to_dataframe(cars: List[Car]) -> pd.DataFrame:
    df = create_cars_dataframe()
    i = 0
    for car in cars:
        df.loc[i] = [
            car.VIN,
            car.Price,
            car.Model.value,
            car.ModelYear,
            car.Drivetrain.value,
            car.ExteriorColor.value,
            car.InteriorColor.value,
            car.Wheels.value,
            car.Mileage,
            car.Location,
            car.VehicleHistory,
        ]
        i += 1
    return df


def to_enum_list(t, l: List[str]):
    return [get_value(t, i) for i in l]


# Daily script that pulls down daily listings for cars
# Only do this query if there isn't a file with today's date in it already


def get_daily_data() -> pd.DataFrame:
    filename = f"{date.today()}.pkl"
    if not path.exists(filename):
        start = time.time()
        msdf = to_dataframe(query(Model.MS, [], [], [], []))
        m3df = to_dataframe(query(Model.M3, [], [], [], []))
        mxdf = to_dataframe(query(Model.MX, [], [], [], []))
        mydf = to_dataframe(query(Model.MY, [], [], [], []))
        end = time.time()

        print(f"Query completed in: {end-start} seconds")

        # Append all the dataframes together

        df = msdf.append(m3df)
        df = df.append(mxdf)
        df = df.append(mydf)

        df = df.reset_index(drop=True)
        df = df.drop_duplicates()
        df = df.set_index("VIN")
        return df
    else:
        return pd.read_pickle(filename)


# Generate synthetic data for n days based on a single day actual dataset


def synthesize_data(
    df, days=10, add_per_day=10, sold_per_day=5, price_adjustment=350
) -> List[pd.DataFrame]:

    # Simulate adding add_per_day new cars per day by removing cars from the 10th day list

    dfs = [df]
    current_df = df
    for _ in range(days):
        rows = len(current_df.index)
        new_df = current_df.sample(frac=((rows - add_per_day) / rows))
        new_df["Price"] = new_df["Price"] - price_adjustment
        dfs.insert(0, new_df)
        current_df = new_df

    # Simulate selling sold_per_day cars by removing cars cumulatively from each list as sold

    sold_list = dfs[0].sample(sold_per_day).index.tolist()
    for i in range(1, len(dfs)):
        dfs[i] = dfs[i].drop(sold_list)
        newly_sold = dfs[i].sample(sold_per_day).index.tolist()
        sold_list += newly_sold

    return dfs


# Next task is to build a new dataframe based query engine using a pair of dataframes
# When working on the synthetic data, which is expressed as a List[pd.DataFrame], we
# will generate two different dataframes. The first is the list of all the cars, along
# with a new Status column that indicates whether the car is: FOR_SALE, SOLD.
# There is another table which contains historical lists of prices, and are joined
# against the cars table.


class Database:
    Cars: pd.DataFrame
    Prices: pd.DataFrame

    def __init__(self):
        self.Cars = create_cars_dataframe()
        self.Prices = create_prices_dataframe()


def create_cars_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "VIN",
            "Price",
            "Model",
            "Year",
            "Drivetrain",
            "Exterior Color",
            "Interior Color",
            "Wheels",
            "Mileage",
            "Location",
            "History",
        ]
    )


def create_prices_dataframe() -> pd.DataFrame:
    return pd.DataFrame(columns=["VIN", "Price", "Date"])


def create_database(data: List[pd.DataFrame]) -> Database:
    filename = "db.pkl"
    if not path.exists(filename):
        db = Database()
        df = pd.read_pickle("2020-11-25.pkl")
        dfs = synthesize_data(df)
        for df in dfs:
            # Add records from df that aren't in db.Cars
            # Add prices from df to db.Prices
            pass

        pickle.dump(db, open(filename, "wb"))
    else:
        db = pickle.load(open(filename, "rb"))
    return db


def update_database(db: Database, data: Union[pd.DataFrame, List[pd.DataFrame]]):
    pass


def update_day(db: Database, data: pd.DataFrame):
    pass
