# Enable debugging in streamlit

from teslahunter import Drivetrain, ExteriorColor, InteriorColor, Wheels, Model
from teslahunter import query, to_dataframe, get_descriptions, to_enum_list, get_value
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
    cars = query(get_value(Model, model),
                 to_enum_list(Drivetrain, drivetrains), 
                 to_enum_list(ExteriorColor, exterior_colors),
                 to_enum_list(InteriorColor, interior_colors), 
                 to_enum_list(Wheels, wheels))
    for car in cars:
        with st.beta_container():
            st.markdown(f"## {car.ModelYear} {car.Drivetrain.value} ${car.Price:,}")
            st.markdown(f"{car.Mileage:,} miles")
            st.markdown(f"{car.ExteriorColor.value} with {car.InteriorColor.value} interior. Located in {car.Location}")
            st.markdown(f"<a target='_blank' href='https://www.tesla.com/used/{car.VIN}'>Order</a>  <a target='_blank' href='https://www.teslacpo.io/vin/{car.VIN}'>Price history</a>", unsafe_allow_html=True)

    data_load_state.text(f"{len(cars)} found.")

    # st.write(to_dataframe(cars))
