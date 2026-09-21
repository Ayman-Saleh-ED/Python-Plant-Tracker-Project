

import streamlit as st 
import pandas as pd
from numpy.random import default_rng as rng

st.write("Testing space? num")








option_map = {
    0: "Add plant",
    1: "Record care",
    2: "Due for care",
    3: "Search plants",
    4: "View all",
}

selection = st.pills(
    "Select an action:",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)

if selection == 0:
    st.subheader("Add a new plant to the collection")
    st.write("Plant-entry form goes here.")

elif selection == 1:
    st.subheader("Record a plant care activity")
    st.write("Care-activity form goes here.")

elif selection == 2:
    st.subheader("View plants due for care")
    st.write("Plants due for care will appear here.")

elif selection == 3:
    st.subheader("Search plants by name or location")
    st.write("Search form goes here.")

elif selection == 4:
    st.subheader("View all plants")
    st.write("All plants will appear here.")