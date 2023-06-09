import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from folium.plugins import MarkerCluster
import folium
import pyproj
from wordcloud import WordCloud
import json
import plotly.graph_objects as go
import requests
import geopandas as gpd
import altair as alt
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import plotly.express as px
import re

st.title('French Hospital Analysis 🇫🇷')
st.subheader("Introduction")
st.write('\nOur analysis is based on hospitals in France and contains information about their locations and specialties, each hospital is represented as a point on the map. \n\nThe dataset includes hospitals with different specialties, and some hospitals may have multiple specialties separated by semicolons. \n\nThe interactive map allows filtering the hospitals based on the selected specialty or showcasing all hospitals.\n\n **Additionally, hospitals without a specified specialty are grouped under the "No Specialty" option.**')
st.write('\n\n')
st.subheader("1 - Overview, General Statistics 🏥")

name = "Talal Eshki"
github_link = "https://github.com/mud00"
linkedin_link = "https://linkedin.com/in/talal-eshki"

st.sidebar.markdown(f"{name}  \n  \nGitHub  \nhttps://www.github.com/mud00  \n  \nLinkedin  \nhttps://www.linkedin.com/in/talal-eshki")

course_name = "Business Intelligence"
course_description = "This is a business intelligence course where we learn about analyzing datasets and showcasing our skills using Streamlit, Python, and analytical techniques."

dataset_name = "French Hospital Dataset"
dataset_description = "The dataset used in this project is sourced from data.gouv and contains information about hospitals in France, including their locations, specialties, and accessibility."

st.sidebar.title("Course Information")
st.sidebar.write(f"Course Name: {course_name}")
st.sidebar.write(f"Course Description: {course_description}")

st.sidebar.title("Dataset Information")
st.sidebar.write(f"Dataset Name: {dataset_name}")
st.sidebar.write(f"Dataset Description: {dataset_description}")
st.sidebar.write("Source: https://www.data.gouv.fr/fr/datasets/localisation-des-hopitaux-dans-openstreetmap/#/resources ")


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

    if not pd.isna(wheelchair):
        wheelchair_counts.append(wheelchair.lower())

    if not pd.isna(amenity):
        if amenity in amenity_counts:
            amenity_counts[amenity] += 1
        else:
            amenity_counts[amenity] = 1

columns_to_drop = ["wikidata", "wikipedia", "description", "opening_hours"]
df = df.drop(columns=columns_to_drop)

average_capacity = sum(capacities) / len(capacities)


sorted_amenity_counts = sorted(amenity_counts.items(), key=lambda x: x[1], reverse=True)

st.markdown(
    """
    <style>
    .metric-container {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
        background-color: #f5f5f5;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 18px;
        color: #808080;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

num_rows = df.shape[0]
average_capacity = round(average_capacity)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="metric-container"><div class="metric-value">{}</div><div class="metric-label">Number of Hospitals</div></div>'.format(num_rows), unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container"><div class="metric-value">{}</div><div class="metric-label">Average Hospital Capacity</div></div>'.format(average_capacity), unsafe_allow_html=True)
                
st.write('\n\n')
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
fig.update_traces(textposition='inside', textinfo='percent+label')
st.caption("We can see that most french hospitals are public, making up approximately **69%** of the hospitals on the region.")



st.write('\n\n')

wheelchair_accessibility_percentage = round((df['wheelchair'].dropna() == 'yes').mean() * 100)
hospital_capacity_mean = round(df['capacity'].dropna().mean())
psychiatric_care_percentage = round((df['healthcare-speciality'].dropna() == 'psychiatry').mean() * 100)



with st.expander("View extra data"):
    st.write("Percentage of Hospitals with Emergency Services:", emergency_services_percentage)
    st.write("Percentage of Hospitals with Wheelchair Accessibility:", wheelchair_accessibility_percentage)
    st.write("Average Hospital Capacity:", hospital_capacity_mean)
    st.write("Percentage of Hospitals Specializing in Psychiatry:", psychiatric_care_percentage)

st.write('\n\n')


st.subheader('2 - In-Depth Analysis: Exploring Key Insights and Specifications')

df['wheelchair'] = df['wheelchair'].str.capitalize()

fig = px.pie(
    df,
    values=df['wheelchair'].value_counts().values,
    names=df['wheelchair'].value_counts().index,
    title="Wheelchair Accessibility Analysis",
    hole=0.6  # Specifies the size of the hole at the center to create a donut chart
)

fig.update_traces(textposition='inside', textinfo='percent+label')

st.plotly_chart(fig)
st.caption("We can see that the **vast majority** of french hospitals have infrastructure that facilitates access to handicapped people.")
st.write('\n\n')
st.write('\n\n')






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
    title="Hospital Speciality Analysis",
    width=600,
    height=500
)

chart = chart.configure_axis(
    labelFontSize=10
)

st.altair_chart(chart)
st.caption("We can see that **intensive care** is the most important, most dominant specialty in french hospitals, occupying the top position with a representation of **36% among all hospitals**.")
st.write('\n\n')
word_weights = {word: count for word, count in zip(labels, counts)}

text = ' '.join([word.title() for word in speciality_values.dropna().tolist()])

wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_weights)

fig, ax = plt.subplots(figsize=(12, 6))
ax.imshow(wordcloud, interpolation='bilinear')
ax.set_axis_off()

st.pyplot(fig)
st.caption("The same data represented as a word cloud.")
st.write('\n\n')
st.write('\n\n')





st.write("**Map of French Hospitals, sorted by specialties and facilities**")
jsonpath = "https://magosm.magellium.com/geoserver/wfs?request=GetFeature&version=2.0.0&count=500000&outputFormat=application/json&typeName=magosm:france_hospitals_point&srsName=EPSG:3857&bbox=-1809724.4405603358,4785559.799771859,2299530.2000507396,7033419.927582323"
response = requests.get(jsonpath)
data = response.json()
hospitals = data['features']

facility_types = set()
no_type_hospitals = []
for hospital in hospitals:
    facility_type = hospital['properties'].get('type-FR-FINESS')
    if facility_type:
        facility_types.update(facility_type.split(';'))
    else:
        no_type_hospitals.append(hospital)

facility_type_options = ['All Facilities'] + [t.title() for t in sorted(facility_types)]
facility_type_options.insert(1, 'No Type')

specialties = set()
no_specialty_hospitals = []
for hospital in hospitals:
    specialty = hospital['properties'].get('healthcare-speciality')
    if specialty:
        specialties.update(specialty.split(';'))
    else:
        no_specialty_hospitals.append(hospital)

specialty_options = ['All Hospitals'] + [s.title() for s in sorted(specialties)]
specialty_options.insert(1, 'No Specialty')

col1, col2 = st.columns(2)

with col1:
    selected_facility_types = st.multiselect("Select Facility Types", facility_type_options)

with col2:
    selected_specialties = st.multiselect("Select Specialties", specialty_options)

filtered_hospitals = hospitals

if selected_facility_types and 'All Facilities' not in selected_facility_types:
    if 'No Type' in selected_facility_types:
        filtered_hospitals = no_type_hospitals
    else:
        filtered_hospitals = [hospital for hospital in hospitals if
                              hospital['properties'].get('type-FR-FINESS') and
                              any(selected.lower() in [t.lower() for t in hospital['properties'].get('type-FR-FINESS').split(';')]
                                  for selected in selected_facility_types)]

if selected_specialties and 'All Hospitals' not in selected_specialties:
    if 'No Specialty' in selected_specialties:
        filtered_hospitals = [hospital for hospital in filtered_hospitals if
                              not hospital['properties'].get('healthcare-speciality')]
    else:
        filtered_hospitals = [hospital for hospital in filtered_hospitals if
                              hospital['properties'].get('healthcare-speciality') and
                              all(selected.lower() in [s.lower() for s in hospital['properties'].get('healthcare-speciality').split(';')]
                                  for selected in selected_specialties)]

in_proj = pyproj.CRS.from_string('EPSG:3857')
out_proj = pyproj.CRS.from_string('EPSG:4326')
transformer = pyproj.Transformer.from_crs(in_proj, out_proj, always_xy=True)

m = folium.Map(location=[48.8566, 2.3522], zoom_start=5, control_scale=True, height='100%')
marker_cluster = MarkerCluster().add_to(m)

for hospital in filtered_hospitals:
    coordinates = hospital['geometry']['coordinates']
    longitude, latitude = transformer.transform(coordinates[0], coordinates[1])
    
    popup_content = "<b>{}</b><br>".format(hospital['properties']['name'])
    specialties = hospital['properties'].get('healthcare-speciality')
    if specialties:
        specialties_list = specialties.split(';')
        popup_content += "<br>".join(specialties_list)
    
    folium.Marker([latitude, longitude], popup=folium.Popup(popup_content)).add_to(marker_cluster)

folium_static(m)
st.write('\n\n')
st.write('\n\n')
st.caption("A "facility" refers to a specific type or category of healthcare institution or service provided by a hospital.")



df = df.dropna(subset=['type-FR-FINESS'])

facility_counts = df['type-FR-FINESS'].value_counts().reset_index()

facility_counts.columns = ['facility', 'count']

sankey_chart = alt.Chart(facility_counts).mark_bar().encode(
    x='count:Q',
    y='facility:N',
    color='facility:N',
    tooltip=['facility:N', 'count:Q']
).properties(
    width=600,
    height=400,    
    title='Healthcare Facility Density',

).interactive()

st.altair_chart(sankey_chart, use_container_width=True)
st.caption("As we can see, facility number 355 is the most common type of hospital, dominating the board with a whopping count of **544 hospitals**.")

df = df.dropna(subset=['capacity'])
