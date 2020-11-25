# Enable debugging in streamlit

from teslahunter import Drivetrain, ExteriorColor, InteriorColor, Wheels
from teslahunter import create_query, query_tesla, to_dataframe, get_descriptions, to_enum_list
import streamlit as st

st.write("""
# tesla-hunter

Power search for used Teslas. Monitor listings and know when to pull the trigger!
""")

drivetrains = st.multiselect(
    'Drivetrain(s):',
    get_descriptions(Drivetrain))

exterior_colors = st.multiselect(
    'Exterior Color(s):',
    get_descriptions(ExteriorColor))

interior_colors = st.multiselect(
    'Interior Color(s):',
    get_descriptions(InteriorColor))

wheels = st.multiselect(
    'Wheels',
    get_descriptions(Wheels))

if st.button("Search!"):
    query = create_query(to_enum_list(Drivetrain, drivetrains), 
                         to_enum_list(ExteriorColor, exterior_colors),
                         to_enum_list(InteriorColor, interior_colors), 
                         to_enum_list(Wheels, wheels))
    cars = query_tesla(query)
    df = to_dataframe(cars)
    st.write(df)