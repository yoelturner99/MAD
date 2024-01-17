import os
from datetime import datetime

from dotenv import load_dotenv
import sqlite3
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set environment variables
load_dotenv()
DATABASE_FILE = os.getenv("DATABASE_FILE")
IMAGES_DIR = os.getenv("IMAGES_DIR")

# Chemin des images
logo_path = f"{IMAGES_DIR}/logoDobby.png"
I1_path = f'{IMAGES_DIR}/total_message.png'
I2_path = f'{IMAGES_DIR}/good_emoji.png'
I3_path = f'{IMAGES_DIR}/bad_emoji.png'
I4_path = f'{IMAGES_DIR}/pourcent.png'
H1_path = f'{IMAGES_DIR}/total_message.png'
H2_path = f'{IMAGES_DIR}/good_emoji.png'
H3_path = f'{IMAGES_DIR}/bad_emoji.png'

def resize_image(image_path: str, size: tuple = (64, 64)) -> Image:
    image = Image.open(image_path)
    image = image.resize(size)
    return image

def calculate_negativity_level(df: pd.DataFrame) -> float:
    total_messages = len(df)
    if total_messages == 0:
        return 0.0
    negative_messages = len(df[df['Sentiment'] == 'haineux'])

    return (negative_messages/total_messages)*100

# Create connection to database
connection = sqlite3.connect(DATABASE_FILE)
# Convert sql database to dataframe
df = pd.read_sql_query("SELECT * FROM messages", connection)
df = df.rename(
    columns={
        "user_id": "User",
        "msg": "Message",
        "label": "Sentiment",
        "msg_type": "MessageType",
        "date": "Timestamp"
    }
)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Date'] = df['Timestamp'].dt.date
df['Time'] = df['Timestamp'].dt.time
# Ajout d'une colonne 'Type' pour distinguer les messages reçus et envoyés
df['Type'] = df.apply(
    lambda row: 'Reçu' if row['User'] != 'UtilisateurActuel'
    else 'Envoyé', axis=1
)


# Définir la couleur de fond et d'autres configurations de page
st.set_page_config(
    page_title='Mon ami Dobby',
    layout='wide',  # Ajuster la mise en page si nécessaire
    initial_sidebar_state='collapsed',
    page_icon=None  # Ajouter l'icône de la page si nécessaire
)

# Ajouter la couleur de fond personnalisée
st.markdown(
    """
    <style>
        body {
            background-color: #4B0082; /* Violet foncé */
            color: white; /* Couleur du texte, changez-la si nécessaire */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# App title
st.title('Mon ami Dobby')
header_left,header_mid,header_right = st.columns([6,1,1],gap='large')
with header_left:
    st.header ("Dashboard du jour")

# App logo in sidebar
img = Image.open(logo_path)
st.sidebar.image(
    image=img,
    caption="Première appli de détéction de cybrharcèlement",
    use_column_width=True
)

# Sidebar
st.sidebar.header('Dashboard ')
tabs = st.sidebar.radio("Navigation", ["Données du jour", "Historique"])


## Création des pages "Donnéesdu jour" et "Historique" ainsi que leur KPI
# Visualization for "Données du jour"
if tabs == "Données du jour":
    indice1, indice2, indice3, indice4 = st.columns(4,gap='large')

    #### Définition de quelques données de base
    # Filtered data for the current day
    filtered_df_today = df[df['Timestamp'].dt.date == datetime.now().date()]
    nombre_messages_positifs = filtered_df_today['Sentiment'].value_counts().get('non haineux', 0)
    nombre_messages_negatifs = filtered_df_today['Sentiment'].value_counts().get('haineux', 0)

    # Redimensionner les images
    resized_image_indice1 = resize_image(I1_path)
    resized_image_indice2 = resize_image(I2_path)
    resized_image_indice3 = resize_image(I3_path)
    resized_image_indice4 = resize_image(I4_path)

    # Création des variables Statitiques du jours (Se referer aux anciens modele)
    # Nombre d'utilisateur
    with indice1:
        st.image(resized_image_indice1, use_column_width='Auto')
        st.metric (label= "Total de message", value = filtered_df_today['User'].nunique() )

    with indice2:
        st.image(resized_image_indice2, use_column_width='Auto')
        st.metric(label="Messages Normaux", value=nombre_messages_positifs)
    
    with indice3:
        st.image(resized_image_indice3, use_column_width='Auto')
        st.metric(label="Messages Haineux", value=nombre_messages_negatifs)
    
    with indice4:
        negativity_percentage = calculate_negativity_level(filtered_df_today)
        st.image(resized_image_indice4 ,use_column_width='Auto')
        st.metric(label="Taux de négativité", value=f"{negativity_percentage:.2f}%")
        #st.write(f"{negativity_percentage:.2f}%")

    # Création de la répartition des messages et de la jauge 
    header_left,header_mid,header_right = st.columns([6,1,1],gap='large')
    with header_left:
        st.header ("Statistiques par utilisateurs")

    Q1,Q2 = st.columns(2, gap='large') #on peut ajouter un Q3

    with Q1:
        # Pie chart for message types
        st.markdown("Répartition des types de messages du jour")
        pie_data_today = filtered_df_today['MessageType'].value_counts()
        st.plotly_chart(px.pie(pie_data_today, names=pie_data_today.index),use_container_width=True)

    with Q2:
        # Création de la figure
        st.markdown("Taux de négativité par utilisateur")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=negativity_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            #delta={'reference': 25},  # Référence pour la jauge de négativité
            #title={'text': f"Niveau de négativité par utilisateur - {selected_user}"},
            gauge={'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 25], 'color': "lightgreen"},
                    {'range': [25, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}
                }
        ))
        # Affichage de la jauge
        st.plotly_chart(fig, title="Niveau de négativité", use_container_width=True)

    # Calcul du nombre total de messages par utilisateur
    total_messages_per_user = df.groupby('User')['Message'].count().reset_index(name='TotalMessages')

    # Calcul du nombre de messages négatifs par utilisateur
    negative_messages_per_user = df[df['Sentiment'] == 'Négatif'].groupby('User')['Message'].count().reset_index(name='NegativeMessages')

    # Fusion des données par utilisateur
    user_data = pd.merge(total_messages_per_user, negative_messages_per_user, on='User', how='left').fillna(0)

    # Calcul du pourcentage de négativité par utilisateur
    user_data['NegativityPercentage'] = (user_data['NegativeMessages'] / user_data['TotalMessages']) * 100

    ## Filtre de la page "Donnée du jour"
    st.sidebar.header("Filtre")
    # Sélection de l'utilisateur actuel
    selected_user = st.sidebar.selectbox("Sélectionnez un utilisateur", user_data['User'])

    # Récupération du pourcentage de négativité pour l'utilisateur sélectionné
    negativity_percentage = user_data[user_data['User'] == selected_user]['NegativityPercentage'].values[0]

    ### Display messages of the day
    st.subheader('Messagerie du jour')
    st.dataframe(filtered_df_today)

# Visualizations for "Historique"
elif tabs == "Historique":
    # Filtres
    st.sidebar.header("Filtres Historique")
    #st.sidebar.subheader("Filtres pour l'historique")
    start_date_hist = st.sidebar.date_input("Date de début", min_value=df['Date'].min(), max_value=df['Date'].max(), value=df['Date'].min())
    end_date_hist = st.sidebar.date_input("Date de fin", min_value=df['Date'].min(), max_value=df['Date'].max(), value=df['Date'].max())
    sentiment_filter = st.sidebar.selectbox("Filtrer par sentiment", df['Sentiment'].unique())
    message_type_filter = st.sidebar.selectbox("Filtrer par type de message", df['MessageType'].unique())
    time_granularity_hist = st.sidebar.selectbox("Granularité temporelle", ['Par heure', 'Par jour', 'Par mois', 'Par année'])

    # Convertir les valeurs en datetime64
    start_date_hist = np.datetime64(start_date_hist)
    end_date_hist = np.datetime64(end_date_hist)

    # Filtrage du DataFrame
    filtered_df_hist = df[
        (df['Date'] >= start_date_hist) &
        (df['Date'] <= end_date_hist) &
        (df['Sentiment'] == sentiment_filter) &
        (df['MessageType'] == message_type_filter)
    ]

    # Statistiques
    st.subheader('Statistiques Historique')

    H1,H2,H3 = st.columns(3, gap='large') 

    nombre_messages_positifs_hist = filtered_df_hist['Sentiment'].value_counts().get('non haineux', 0)
    nombre_messages_negatifs_hist = filtered_df_hist['Sentiment'].value_counts().get('haineux', 0)
    
    # Redimensionner les images
    resized_image_H1 = resize_image(H1_path)
    resized_image_H2 = resize_image(H2_path)
    resized_image_H3 = resize_image(H3_path)

    with H1:
        st.image(resized_image_H1,use_column_width='Auto')
        st.metric (label= "Nombre total de messages", value = len(filtered_df_hist))

    with H2:
        st.image(resized_image_H2,use_column_width='Auto')
        st.metric(label="Nombre de messages positifs", value=nombre_messages_positifs_hist)
    
    with H3:
        st.image(resized_image_H3,use_column_width='Auto')
        st.metric(label="Nombre de messages négatifs", value=nombre_messages_negatifs_hist)

    Q4,Q5 = st.columns([1,2], gap='large')

    # Pie chart pour les types de messages
    with Q4:
        st.subheader("Répartition des messages par types")
        pie_data_hist = filtered_df_hist['MessageType'].value_counts()
        st.plotly_chart(px.pie(pie_data_hist, names=pie_data_hist.index), use_container_width=True)

    # Graphique temporel
    with Q5 :
        st.subheader("Analyse des messageries au cours du temps")
        if time_granularity_hist == 'Par heure':
                grouped_data_hist = filtered_df_hist.groupby(['Sentiment', pd.Grouper(key='Timestamp', freq='H')]).size().reset_index(name='Count')
        elif time_granularity_hist == 'Par jour':
            grouped_data_hist = filtered_df_hist.groupby(['Sentiment', pd.Grouper(key='Timestamp', freq='D')]).size().reset_index(name='Count')
        elif time_granularity_hist == 'Par mois':
            grouped_data_hist = filtered_df_hist.groupby(['Sentiment', pd.Grouper(key='Timestamp', freq='M')]).size().reset_index(name='Count')
        else:  # Par année par défaut
            grouped_data_hist = filtered_df_hist.groupby(['Sentiment', pd.Grouper(key='Timestamp', freq='Y')]).size().reset_index(name='Count')

        # Création du graphique
        fig_hist = px.line(grouped_data_hist, x='Timestamp', y='Count', color='Sentiment', markers=True, line_dash="Sentiment",
                        #title='Analyse des messageries au cours du temps',
                        labels={'Count': 'Nombre de Messages', 'Timestamp': 'Date'})

        # Affichage du graphique 
        st.plotly_chart(fig_hist, use_container_width=True)
        