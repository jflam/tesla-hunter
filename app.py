# Enable debugging in streamlit

from teslahunter import Drivetrain, ExteriorColor, InteriorColor, Wheels, Model
from teslahunter import create_query, query_tesla, to_dataframe, get_descriptions, to_enum_list, get_value
import streamlit as st

'''
# tesla-hunter

Power search for used Teslas. Monitor listings and know when to pull the trigger!
'''

model = st.sidebar.selectbox(
    'Model',
    get_descriptions(Model))

drivetrains = st.sidebar.multiselect(
    'Drivetrain(s):',
    get_descriptions(Drivetrain))

exterior_colors = st.sidebar.multiselect(
    'Exterior Color(s):',
    get_descriptions(ExteriorColor))

interior_colors = st.sidebar.multiselect(
    'Interior Color(s):',
    get_descriptions(InteriorColor))

wheels = st.sidebar.multiselect(
    'Wheels',
    get_descriptions(Wheels))

if st.sidebar.button("Search!"):
    data_load_state = st.text('Running query ...')
    query = create_query(get_value(Model, model),
                         to_enum_list(Drivetrain, drivetrains), 
                         to_enum_list(ExteriorColor, exterior_colors),
                         to_enum_list(InteriorColor, interior_colors), 
                         to_enum_list(Wheels, wheels))
    cars = query_tesla(query)
    data_load_state.text('Done!')
    st.write(to_dataframe(cars))
