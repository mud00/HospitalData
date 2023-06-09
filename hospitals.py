import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from folium.plugins import MarkerCluster
import folium
import pyproj
import json
import requests
import geopandas as gpd
import altair as alt
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import plotly.express as px
import re

st.title('French Hospital Analysis 🇫🇷 🏥')
st.header("Introduction:")
st.write('\nOur analysis is based on hospitals in France and contains information about their locations and specialties, each hospital is represented as a point on the map. \n\nThe dataset includes hospitals with different specialties, and some hospitals may have multiple specialties separated by semicolons. \n\nThe interactive map allows filtering the hospitals based on the selected specialty or showcasing all hospitals.\n\n **Additionally, hospitals without a specified specialty are grouped under the "No Specialty" option.**')
st.subheader('Summary Statistics')


name = "Talal Eshki"
github_link = "https://github.com/mud00"
linkedin_link = "https://linkedin.com/in/talal-eshki"
st.sidebar.markdown(f"{name}  \n  \nGitHub  \nhttps://www.github.com/mud00  \n  \nLinkedin  \nhttps://www.linkedin.com/in/talal-eshki")



path = "https://magosm.magellium.com/geoserver/wfs?request=GetFeature&version=2.0.0&count=500000&outputFormat=csv&typeName=magosm:france_hospitals_point&srsName=EPSG:3857&bbox=-1809724.4405603358,4785559.799771859,2299530.2000507396,7033419.927582323"
df = pd.read_csv(path, delimiter=",")

capacities = []
wheelchair_counts = []
amenity_counts = {}

for _, row in df.iterrows():
    capacity = row['capacity']
    wheelchair = row['wheelchair']
    amenity = row['amenity']

    if not pd.isna(capacity):
        capacities.append(int(capacity))

    # Count the number of wheelchair accessible hospitals
    if not pd.isna(wheelchair):
        wheelchair_counts.append(wheelchair.lower())

    # Count the number of hospitals by amenity
    if not pd.isna(amenity):
        if amenity in amenity_counts:
            amenity_counts[amenity] += 1
        else:
            amenity_counts[amenity] = 1

columns_to_drop = ["wikidata", "wikipedia", "description", "opening_hours"]
df = df.drop(columns=columns_to_drop)

# Calculate the average capacity of hospitals
average_capacity = sum(capacities) / len(capacities)


sorted_amenity_counts = sorted(amenity_counts.items(), key=lambda x: x[1], reverse=True)

num_rows = df.shape[0]

st.write("Number of Hospitals:", num_rows)
st.write("Average Capacity:", round(average_capacity))

emergency_services_percentage = round((df['emergency'].dropna() == 'yes').mean() * 100)







filtered_df = df[df['operator-type'].isin(['public', 'private'])]

operator_type_distribution = filtered_df['operator-type'].value_counts()

operator_type_distribution.index = operator_type_distribution.index.str.capitalize()

fig = px.pie(
    operator_type_distribution,
    values=operator_type_distribution.values,
    names=operator_type_distribution.index,
    title="Public vs. Private Hospital Distribution"
)
st.plotly_chart(fig)
st.caption("We can see that most french hospitals are public, making up approximately 69% of the hospitals on the region.")




st.write("Percentage of Hospitals with Emergency Services:", emergency_services_percentage)



wheelchair_accessibility_percentage = round((df['wheelchair'].dropna() == 'yes').mean() * 100)
st.write("Percentage of Hospitals with Wheelchair Accessibility:", wheelchair_accessibility_percentage)



hospital_capacity_mean = round(df['capacity'].dropna().mean())
st.write("Average Hospital Capacity:", hospital_capacity_mean)





psychiatric_care_percentage = round((df['healthcare-speciality'].dropna() == 'psychiatry').mean() * 100)
st.write("Percentage of Hospitals Specializing in Psychiatry:", psychiatric_care_percentage)




hospital_names = df['name'].unique()
alt_names_count = df['alt_name'].nunique()
st.write("Number of Unique Hospital Names:", len(hospital_names))
st.write("Number of Unique Alternative Names:", alt_names_count)


st.subheader('Wheelchair Accessibility Analysis')

df['wheelchair'] = df['wheelchair'].str.capitalize()

fig = px.pie(
    df,
    values=df['wheelchair'].value_counts().values,
    names=df['wheelchair'].value_counts().index,
    title="Wheelchair Accessibility Analysis"
)

st.plotly_chart(fig)








df_filtered = df.dropna(subset=['healthcare-speciality'])

speciality_values = df_filtered['healthcare-speciality'].str.split(';').explode()

speciality_counts = speciality_values.value_counts()

threshold = len(df_filtered) * 0.021

top_specialities = speciality_counts[speciality_counts >= threshold]

other_specialities_count = speciality_counts[speciality_counts < threshold].sum()
top_specialities['Other'] = other_specialities_count

labels = [word.title() for word in top_specialities.index]

counts = list(top_specialities.values)

chart_data = pd.DataFrame({'Speciality': labels, 'Count': counts})
sorted_data = chart_data.sort_values('Count', ascending=False)  # Sort the data by Count in descending order

total_count = chart_data['Count'].sum()
chart_data['Percentage'] = (chart_data['Count'] / total_count) * 100

sorted_data = chart_data.sort_values('Percentage', ascending=False)

filtered_data = sorted_data[sorted_data['Speciality'] != 'Other']

chart = alt.Chart(filtered_data).mark_bar().encode(
    x=alt.X('Percentage:Q', axis=alt.Axis(format='.1f', title='Percentage')),
    y=alt.Y('Speciality:N', sort=alt.EncodingSortField(field='Percentage', order='descending'),
            axis=alt.Axis(title='Speciality', labelAngle=0)),  # Set labelAngle=0 to rotate the labels horizontally
).properties(
    width=600,
    height=500
)

chart = chart.configure_axis(
    labelFontSize=10
)

st.altair_chart(chart)







jsonpath = "https://magosm.magellium.com/geoserver/wfs?request=GetFeature&version=2.0.0&count=500000&outputFormat=application/json&typeName=magosm:france_hospitals_point&srsName=EPSG:3857&bbox=-1809724.4405603358,4785559.799771859,2299530.2000507396,7033419.927582323"
response = requests.get(jsonpath)
data = response.json()
hospitals = data['features']

specialties = set()
no_specialty_hospitals = []
for hospital in hospitals:
    specialty = hospital['properties'].get('healthcare-speciality')
    if specialty:
        specialties.update(specialty.split(';'))
    else:
        no_specialty_hospitals.append(hospital)

specialty_options = ['All Hospitals'] + [s.title() for s in specialties]
specialty_options.insert(1, 'No Specialty')
selected_specialty = st.selectbox("Select Specialty", specialty_options)

filtered_hospitals = hospitals
if selected_specialty != 'All Hospitals':
    if selected_specialty == 'No Specialty':
        filtered_hospitals = no_specialty_hospitals
    else:
        filtered_hospitals = [hospital for hospital in hospitals if
                              hospital['properties'].get('healthcare-speciality') and
                              selected_specialty.lower() in [s.lower() for s in hospital['properties'].get('healthcare-speciality').split(';')]]

in_proj = pyproj.CRS.from_string('EPSG:3857')
out_proj = pyproj.CRS.from_string('EPSG:4326')
transformer = pyproj.Transformer.from_crs(in_proj, out_proj, always_xy=True)

m = folium.Map(location=[48.8566, 2.3522], zoom_start=5, control_scale=True, height='100%')
marker_cluster = MarkerCluster().add_to(m)

for hospital in filtered_hospitals:
    coordinates = hospital['geometry']['coordinates']
    longitude, latitude = transformer.transform(coordinates[0], coordinates[1])
    folium.Marker([latitude, longitude], popup=hospital['properties']['name']).add_to(marker_cluster)

folium_static(m)
