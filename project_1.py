import streamlit as st 
import pandas as pd
from numpy.random import default_rng as rng
import p1_utils as utils




option_map = {
    0: "Add plant",
    1: "Record care",
    2: "Due for care",
    3: "Search plants",
    4: "View all",
    5: "Growth measurement",
    6: "Seasonal tips",
    7: "Add photo of plant",
    8: "Plant problem diagnosis",
    9: "AI Plant Doctor",
}
selection = st.pills(
    "Select what you want to do:",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)
if selection == 0:
    st.subheader("Add a new plant to the collection")

    plnt_name = st.text_input("Plant Name/Species")
    
    fetched_info = None
    if plnt_name:
        fetched_info = utils.fetch_plant_info(plnt_name)
        if fetched_info:
            st.info(f"Found info: {fetched_info['care_tip']}")
        else:
            st.write("No match found fill in details manually.")

    plnt_type = st.selectbox("Plant Type", ["Fruit", "Herb", "Flowering plant", "Palm", "Cactus"])
    plnt_location = st.text_input("Plant Location in Home")
    plnt_date = st.date_input("Plant Date of Purchase")
    plnt_water_freq = st.number_input("How many days should pass between waterings for this plant?", min_value=1, max_value=30, value=2)
    plnt_sunlight = st.selectbox("Sunlight Requirements", ["Low", "Medium", "High"])

    if st.button("Add Plant"):
        new_plant = pd.DataFrame({
            "name": [plnt_name],
            "plant_type": [plnt_type],
            "location": [plnt_location],
            "date_of_purchase": [plnt_date],
            "watering_frequency": [plnt_water_freq],
            "sunlight_requirements": [plnt_sunlight],
        })
        utils.add_plant(new_plant)
        st.success(f"Plant '{plnt_name}' added successfully!")


elif selection == 1:
    st.subheader("Record a plant care activity")

    care_plnt = st.selectbox("Plant Cared for", utils.load_plant_data()['name']) #add list of plant names from the plant data
    care_type = st.selectbox("Type of Care", ["Watering", "Fertilizing", "Pruning", "Repotting"])
    date_care = st.date_input("Date of Care")

    if st.button("Record Care"):
        new_care = pd.DataFrame({
            "plant_name": [care_plnt],
            "care_type" : [care_type],
            "date_of_care": [date_care]

        })
        utils.record_care(new_care)
        st.success(f"Care for {care_plnt} Recorded successfully")

    

elif selection == 2:
    st.subheader("View plants due for care")
    due = utils.plants_due_for_care()
    if due.empty:
        st.write("No plants need care right now!")
    else:
        note = utils.get_seasonal_watering_note()
        st.info(note)
        st.dataframe(due)

elif selection == 3:
    st.subheader("Search plants by name or location")
    
   # search_term = st.text_input("Search by Name/location")
    #st.subheader("Search plants by name or location")
    search_term = st.text_input("Search by Name/location")
    if search_term:
        results = utils.search_plants(search_term)
        st.dataframe(results)

elif selection == 4:
    st.subheader("View all plants")

    st.dataframe(utils.load_plant_data())

elif selection == 5:
    st.subheader("Record Growth Measurement for a Plant")

    growth_plnt = st.selectbox("Plant to record growth for", utils.load_plant_data()['name']) #add list of plant names from the plant data
    growth = st.number_input("Measurement (cm)", min_value=0.0, step=0.1)
    measure_date = st.date_input("Date of Measurement")

    if st.button("Record Growth Measurement"):
        new_growth = pd.DataFrame({
            "plant_name": [growth_plnt],
            "measurement": [growth],
            "date_of_measurement": [measure_date]
        })
        utils.record_growth(new_growth)
        st.success(f"Growth measurement for {growth_plnt} recorded successfully!")


elif selection == 6:
    st.subheader("Seasonal Tips")
    season = utils.get_season()
    st.write(f"Current season: {season}")

    all_plants = utils.load_plant_data()
    if all_plants.empty:
        st.write("No plants added yet!")
    else:
        for index, plant in all_plants.iterrows():
            tip = utils.get_seasonal_tip(plant['plant_type'])
            st.write(f"{plant['name']}: {tip}")

elif selection == 7:
    st.subheader("Add a photo of a plant")
    plant_name = st.selectbox("Select Plant", utils.load_plant_data()['name'])
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        utils.save_plant_photo(plant_name, uploaded_file)
        st.success(f"Photo for {plant_name} saved successfully!")

elif selection == 8:
    st.subheader("Plant Problem Diagnosis")
    
    diag_plnt = st.selectbox("Which plant?", utils.load_plant_data()['name'])
    symptoms = st.multiselect("Select observed symptoms", list(utils.symptom_diagnoses.keys()))
    
    if symptoms:
        results = utils.diagnose_symptoms(symptoms)
        for symptom, advice in results.items():
            st.write(f"{symptom}: {advice}")


elif selection == 9:
    ai_plant = str(st.selectbox("Which plant do you need help with?", utils.load_plant_data()['name']))
    ai_symptoms = st.text_area("Enter symptoms:")
    care_history = utils.load_care_data()

    plant_care_history = care_history[care_history['plant_name'] == ai_plant]
    plant_care_history_str = str(plant_care_history)

    prompt = f"You are an AI plant care advisor. The user has a plant named '{ai_plant}' with the following symptoms: {ai_symptoms}. The care history for this plant is as follows: {plant_care_history_str}. Please provide advice on how to care for this plant based on the symptoms and care history."
    if st.button("Get AI Advice"):
        with st.status("Generating advice..."):
            ai_response = utils.get_llm_response(prompt)
        st.write(ai_response)



