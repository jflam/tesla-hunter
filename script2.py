# Another take on the code, partially refactored into teslatypes.py

#%%

# Custom enum types to make the options work better

import enum

class EnumValue:
    value : str
    description : str 

    def __init__(self, value : str, description : str):
        self.value = value 
        self.description = description

class ExteriorColor(enum.Enum):
    RED = EnumValue('RED', 'Red Multi-Coat')
    WHITE = EnumValue('WHITE', 'Pearl White Multi-Coat')
    SILVER = EnumValue('SILVER', 'Silver Metallic')
    BLUE = EnumValue('BLUE', 'Deep Blue Metallic')
    BLACK = EnumValue('BLACK', 'Solid Black')
    GRAY = EnumValue('GRAY', 'Midnight Silver Metallic')
    UNKNOWN = EnumValue('UNKNOWN', 'Unknown Exterior Color')

class InteriorColor(enum.Enum):
    BLACK = EnumValue('PREMIUM_BLACK', 'Premium Black')
    WHITE = EnumValue('PREMIUM_WHITE', 'Premium Black and White')
    UNKNOWN = EnumValue("UNKNOWN", 'Unknown Interior Color')

class Drivetrain(enum.Enum):
    LRAWD = EnumValue('LRAWD', "Long Range AWD")
    LRAWDP = EnumValue('LRAWDP', "Long Range AWD Performance")
    LRRWD = EnumValue('LRRWD', "Long Range RWD")
    MRRWD = EnumValue('MRRWD', "Medium Range RWD")
    SRPRWD = EnumValue('SRPRWD', "Standard Range Plus RWD")
    UNKNOWN = EnumValue("UNKNOWN", 'Unknown Drivetrain')

class Wheels(enum.Enum):
    EIGHTEEN = EnumValue('EIGHTEEN', '18" Aero Wheels')
    NINETEEN = EnumValue('NINETEEN', '19" Sport Wheels')
    TWENTY = EnumValue('TWENTY', '20" Fragile Wheels')
    UNKNOWN = EnumValue('Unknown', "Unknown Wheel Type")

# Return descriptions for UX

def get_descriptions(t):
    return [v.value.description for v in t]

# Lookup an Enum value based on the description

def get_value(t, description : str):
    for e in t:
        if e.value.description == description:
            return e
    return t.UNKNOWN # this is by convention

# %%

import enum

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
        if e.value == description:
            return e
    print(f"Unknown {description} while looking up {t}")
    return t.UNKNOWN # this is by convention

# %%
import teslatypes as tt

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
