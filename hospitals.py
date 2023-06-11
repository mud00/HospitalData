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

facility_names = {
  101: "Centre Hospitalier Régional",
  106: "Centre Hospitalier ex Hôpital local",
  109: "Soins de Suite et Réadaptation",
  114: "Hôpital des armées",
  122: "Établissement de Soins Obstétriques Chirurgico-Gynécologiques",
  124: "Centre de Santé",
  125: "Centre de Santé Dentaire",
  126: "Établissement Thermal",
  128: "Établissement de Soins Chirurgicaux",
  129: "Établissement de Soins Médicaux",
  131: "Centre de Lutte Contre le Cancer",
  132: "Établissement de Transfusion Sanguine",
  141: "Centre de Dialyse",
  156: "Centre Médico-Psychologique",
  177: "Maison d'enfants à caractère social",
  183: "Institut Médico-Educatif",
  186: "Institut Thérapeutique, Éducatif et Pédagogique",
  189: "Centre médico-psycho-pédagogique",
  202: "Établissement d'hébergement pour personnes agées",
  219: "Autre Centre d'Accueil",
  223: "Protection Maternelle et Infantile",
  246: "Établissement et Service d'Aide par le Travail",
  255: "Maison d'Accueil Spécialisée",
  266: "Centre gratuit d’information, de dépistage et de diagnostic",
  289: "Centre de Soins Infirmiers",
  292: "Centre Hospitalier Spécialisé lutte Maladies Mentales",
  355: "Centre hospitalier",
  362: "Établissement de Soins Longue Durée",
  365: "Établissement de Soins Pluridisciplinaire",
  374: "École des Hautes Etudes en Santé Publique",
  425: "Centre d'Accueil Thérapeutique à Temps Partiel",
  436: "Écoles Formant aux Professions Sanitaires et Sociales",
  437: "Foyer d'Accueil Médicalisé pour Adultes Handicapés",
  443: "Centre d'Accueil de Demandeurs d'Asile",
  500: "Établissement d'hébergement pour personnes âgées dépendantes Maison de retraite médicalisée",
  501: "Établissement d'hébergement pour personnes âgées Maison de retraite non médicalisée",
  502: "Établissement d'hébergement pour personnes âgées Maison de retraite non médicalisée",
  603: "Maison de Santé",
  610: "Laboratoire d'Analyses",
  611: "Laboratoire de Biologie Médicale",
  620: "Pharmacie d'officine"
}

st.title('French Medical Institution Analysis')
st.subheader("Introduction 🇫🇷")
st.write('\nOur analysis is based on medical centers in France and contains information about their locations and specialties, each institution is represented as a point on the map. \n\nThe dataset includes institutions with different specialties, and some establishments may have multiple specialties separated by semicolons. \n\nThe interactive map allows filtering the institutions based on the selected specialty or showcasing all institutions.\n\n **Additionally, establishments without a specified specialty are grouped under the "No Specialty" option.**')
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
    st.markdown('<div class="metric-container"><div class="metric-value">{}</div><div class="metric-label">Number of Institutions</div></div>'.format(num_rows), unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container"><div class="metric-value">{}</div><div class="metric-label">Average Institution Capacity</div></div>'.format(average_capacity), unsafe_allow_html=True)
                
st.write('\n\n')
emergency_services_percentage = round((df['emergency'].dropna() == 'yes').mean() * 100)






filtered_df = df[df['operator-type'].isin(['public', 'private'])]

operator_type_distribution = filtered_df['operator-type'].value_counts()

operator_type_distribution.index = operator_type_distribution.index.str.capitalize()

fig = px.pie(
    operator_type_distribution,
    values=operator_type_distribution.values,
    names=operator_type_distribution.index,
    title="Public vs. Private Establishment Distribution"
)
st.plotly_chart(fig)
fig.update_traces(textposition='inside', textinfo='percent+label')
st.caption("We can see that most french medical institutions are public, making up approximately **69%** of the hospitals on the region.")



st.write('\n\n')

wheelchair_accessibility_percentage = round((df['wheelchair'].dropna() == 'yes').mean() * 100)
hospital_capacity_mean = round(df['capacity'].dropna().mean())
psychiatric_care_percentage = round((df['healthcare-speciality'].dropna() == 'psychiatry').mean() * 100)



with st.expander("View extra data"):
    st.write("Percentage of Institutions with Emergency Services:", emergency_services_percentage)
    st.write("Percentage of Institutions with Wheelchair Accessibility:", wheelchair_accessibility_percentage)
    st.write("Average Institution Capacity:", hospital_capacity_mean)
    st.write("Percentage of Institutions Specializing in Psychiatry:", psychiatric_care_percentage)

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
st.caption("We can see that the **vast majority** of french medical institutions have infrastructure that facilitates access to handicapped people.")
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

chart = alt.Chart(filtered_data).mark_bar().encoxde(
    x=alt.X('Percentage:Q', axis=alt.Axis(format='.1f', title='Percentage')),
    y=alt.Y('Speciality:N', sort=alt.EncodingSortField(field='Percentage', order='descending'),
            axis=alt.Axis(title='Speciality', labelAngle=0)),  # Set labelAngle=0 to rotate the labels horizontally
).properties(
    title="Institution Speciality Analysis",
    width=600,
    height=500
)

chart = chart.configure_axis(
    labelFontSize=10
)

st.altair_chart(chart)
st.caption("We can see that **intensive care** is the most important, most dominant speciality in french medical institutions, occupying the top position with a representation of **36% among all hospitals**.")
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

facility_data = {'Type Code': [], 'Facility Name': []}

for code, name in facility_names.items():
    facility_data['Type Code'].append(code)
    facility_data['Facility Name'].append(name)

df_2 = pd.DataFrame(facility_data)

with st.expander("View facility references"):
  st.table(df_2)

st.write("\n\n")
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
facility_type_options = ['All Facilities'] + [facility_names.get(int(t), '') for t in sorted(facility_types) if t.isdigit()]
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

st.caption('A "**facility**" refers to a specific type or category of healthcare institution.')
st.write('\n\n')



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
st.caption("As we can see, facility number 355, so Hospital Centers, are the most common type of medical institution, dominating the board with a whopping count of **544 hospitals**.")

df = df.dropna(subset=['capacity'])
