import streamlit as st
import pandas as pd
import os
import datetime as dt
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

open_api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=open_api_key
)


#def load_data():
 #   if os.path.exists('plants.csv'):
  #      return pd.read_csv('plants.csv')
   # else:
    #    return pd.DataFrame(columns=["", "", "", "", ""])





# Plant addition

def load_plant_data():
    if os.path.exists('plants.csv'):
        try:
            return pd.read_csv('plants.csv')
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["name", "location", "date_of_purchase", "watering_frequency", "sunlight_requirements"])
    else:
        return pd.DataFrame(columns=["name", "location", "date_of_purchase", "watering_frequency", "sunlight_requirements"])

    
def add_plant(new_plant_df):
    '''
    Add the plant to the csv.
    '''
    old = load_plant_data()
    new = pd.concat([old, new_plant_df])
    new.to_csv('plants.csv', index=False)


#Plant care

def load_care_data():
    if os.path.exists('care_data.csv'):
        try:
            return pd.read_csv('care_data.csv')
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["plant_name", "care_type", "date_of_care"])
    else:
        return pd.DataFrame(columns=["plant_name", "care_type", "date_of_care"])


def record_care(care_df):
   old = load_care_data()
   new = pd.concat([old, care_df])
   new.to_csv('care_data.csv', index=False)


#Due for care


def plants_due_for_care():
    plant_df = load_plant_data()
    care_df = load_care_data()
    today = dt.date.today()
     # care_date = pd.to_datetime(care_df['date_of_care'])
    
    due_plants= []
    
    for index, plant in plant_df.iterrows():
        plant_name = plant['name']
        watering_freq = plant['watering_frequency']
        
        plant_waterings = care_df[(care_df['plant_name'] == plant_name) & (care_df['care_type'] == 'Watering')]
        
        if plant_waterings.empty:
            due_plants.append(plant)
        else:                                                   #max for latest & date so we make it into date without time part
            last_watered = pd.to_datetime(plant_waterings['date_of_care']).max().date()  
            days_since = (today - last_watered).days
            if days_since >= watering_freq:
                due_plants.append(plant)
    
    return pd.DataFrame(due_plants)


#search plants

def search_plants(term):
    plant_df = load_plant_data()
    term = term.lower()
    matches = plant_df[
        plant_df['name'].str.lower().str.contains(term) |
        plant_df['location'].str.lower().str.contains(term)
    ]
    return matches


# Growth measurement


def load_growth_data():
    if os.path.exists('growth_data.csv'):
        try:
            return pd.read_csv('growth_data.csv')
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["plant_name", "measurement", "date_of_measurement", "photo_path"])
    else:
        return pd.DataFrame(columns=["plant_name", "measurement", "date_of_measurement", "photo_path"])

def record_growth(growth_df):
    old = load_growth_data()
    new = pd.concat([old, growth_df])
    new.to_csv('growth_data.csv', index=False)


#Seasonal stuff

def get_season():
    month = dt.date.today().month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"



seasonal_tips = {
    ("Fruit", "Winter"): "Growth slows — reduce watering and hold off on fertilizing until spring.",
    ("Fruit", "Spring"): "Active growth begins — resume regular feeding and watering.",
    ("Fruit", "Summer"): "Peak growing season — water consistently and watch for pests.",
    ("Fruit", "Fall"): "Growth slows — start tapering off fertilizer as the plant prepares for dormancy.",

    ("Herb", "Winter"): "Lower light indoors slows growth — water less and expect slower harvests.",
    ("Herb", "Spring"): "Great time to start new herbs — increase watering as growth picks up.",
    ("Herb", "Summer"): "Peak growth — water frequently and harvest often to encourage new growth.",
    ("Herb", "Fall"): "Growth slows with shorter days — reduce watering frequency.",

    ("Flowering plant", "Winter"): "Most flowering plants rest now — reduce watering and skip fertilizer.",
    ("Flowering plant", "Spring"): "Bloom season approaching — resume feeding to support flowers.",
    ("Flowering plant", "Summer"): "Active blooming — water regularly and deadhead spent flowers.",
    ("Flowering plant", "Fall"): "Blooming slows — gradually reduce watering and feeding.",

    ("Palm", "Winter"): "Growth slows — let soil dry out more between waterings.",
    ("Palm", "Spring"): "Growth resumes — increase watering gradually.",
    ("Palm", "Summer"): "Peak growth — keep soil consistently moist, not soggy.",
    ("Palm", "Fall"): "Growth slows — start reducing watering frequency.",

    ("Cactus", "Winter"): "Dormant season — water very sparingly, only if soil is fully dry.",
    ("Cactus", "Spring"): "Growth resumes — gradually increase watering.",
    ("Cactus", "Summer"): "Active growth — water when soil is fully dry, but don't overdo it.",
    ("Cactus", "Fall"): "Growth slows — cut back watering as it prepares for winter dormancy.",
}

def get_seasonal_tip(plant_type):
    season = get_season()
    return seasonal_tips.get((plant_type, season), f"No  {season.lower()} tip for this plant type, monitor as usual.")


#Photo upload

def save_plant_photo(plant_name, uploaded_file):
    if not os.path.exists('photos'):
        os.makedirs('photos')
    
    photo_path = f"photos/{plant_name}_{uploaded_file.name}"
    
    with open(photo_path, 'wb') as f:               #write binary, so that we can save the image file correctly not as text
        f.write(uploaded_file.getbuffer())
    
    new_photo = pd.DataFrame({
        "plant_name": [plant_name],
        "measurement": [None],
        "date_of_measurement": [None],
        "photo_path": [photo_path]
    })
    
    old = load_growth_data()
    new = pd.concat([old, new_photo], ignore_index=True)
    new.to_csv('growth_data.csv', index=False)


#Adjust watering based on season 


season_watering_notes = {
    "Winter": "Consider reducing watering amount — growth typically slows in winter.",
    "Spring": "Growth is picking up — normal watering should be fine.",
    "Summer": "Consider increasing watering amount — heat increases water needs.",
    "Fall": "Growth is slowing — you may reduce watering slightly.",
}

def get_seasonal_watering_note():
    season = get_season()
    return season_watering_notes[season]


#diagnose plant symptoms

symptom_diagnoses = {
    "Yellow leaves": "Often caused by overwatering or poor drainage. Let soil dry out more between waterings.",
    "Brown leaf tips": "Usually low humidity or a buildup of salts/minerals from tap water. Try filtered water and misting.",
    "Wilting despite moist soil": "Could be root rot from overwatering, or roots outgrowing the pot. Check for mushy roots.",
    "Wilting with dry soil": "Simple underwatering — increase watering frequency.",
    "Dropping leaves": "Often stress from sudden changes — temperature, light, or being moved recently.",
    "Leggy/stretched growth": "Usually not enough light — the plant is stretching toward a light source.",
    "Spots on leaves": "Could be fungal issues from overhead watering, or sunburn from too much direct light.",
    "No growth": "May be dormant (normal in winter) or root-bound — consider repotting if soil is depleted.",
}

def diagnose_symptoms(selected_symptoms):
    results = {}
    for symptom in selected_symptoms:
        results[symptom] = symptom_diagnoses.get(symptom, "No specific advice available.")
    return results


    
   



# 1. Initialize the client (API key + Base URL) 🔑
# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("OPENROUTER_API_KEY")
# )


def get_llm_response(prompt):
    completion = client.chat.completions.create(
        model="cohere/north-mini-code:free",
        messages=[
            {
                "role": "system",
                "content": "for the given plant, generate a diagnostic report and step-by-step recovery plan.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    response = completion.choices[0].message.content
    return response


#API data

import requests

def fetch_plant_info(species_name):
    url = "https://trefle.io/api/v1/plants/search"
    params = {"token": st.secrets.get("TREFLE_TOKEN", os.getenv("TREFLE_TOKEN")), "q": species_name}
    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("data"):
            plant = data["data"][0]
            main_species = plant.get("main_species", {})
            growth = main_species.get("growth", {}) if main_species else {}
            
            common_name = plant.get("common_name")
            family = plant.get("family_common_name")
            light = growth.get("light")
            watering = growth.get("atmospheric_humidity")
            
            tip_parts = []
            if common_name:
                tip_parts.append(f"Common name: {common_name}.")
            if family:
                tip_parts.append(f"Family: {family}.")
            if light:
                tip_parts.append(f"Light requirement (1-10 scale): {light}.")
            if watering:
                tip_parts.append(f"Humidity preference (1-10 scale): {watering}.")
            
            if not tip_parts:
                tip_parts.append("Species matched, but no detailed care data available — fill in manually below.")
            
            care_tip = " ".join(tip_parts)
            
            return {
                "watering": watering if watering else "Unknown",
                "sunlight": light if light else "Unknown",
                "care_tip": care_tip
            }
        else:
            return None
    except Exception:
        return None


    
