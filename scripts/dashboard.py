import os
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
import plotly.graph_objects as go

# Set environment variables
load_dotenv()
DATABASE_FILE = os.getenv("DATABASE_FILE")
IMAGES_DIR = os.getenv("IMAGES_DIR")
THRESHOLD =  int(os.getenv("THRESHOLD"))

# Images path
logo_path = f"{IMAGES_DIR}/logoDobby.png"
I1_path = f'{IMAGES_DIR}/total_message.png'
I2_path = f'{IMAGES_DIR}/good_emoji.png'
I3_path = f'{IMAGES_DIR}/bad_emoji.png'
I4_path = f'{IMAGES_DIR}/pourcent.png'
H1_path = f'{IMAGES_DIR}/total_message.png'
H2_path = f'{IMAGES_DIR}/good_emoji.png'
H3_path = f'{IMAGES_DIR}/bad_emoji.png'
H4_path = f'{IMAGES_DIR}/pourcent.png'

def resize_image(image_path: str, size: tuple = (64, 64)) -> Image:
    image = Image.open(image_path)
    image = image.resize(size)
    return image

# Fonction de la dernière date d'actualisation 
def get_last_update_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function calcul niveau de négativité
def calculate_negativity_level(df):
    total_messages = len(df)
    if total_messages == 0:
        return 0.0
    else:
        negative_messages = len(df[df['label'] == 'haineux'])
        negativity_percentage = (negative_messages / total_messages) * 100
        return negativity_percentage


# Create connection to database
connection = sqlite3.connect(DATABASE_FILE)
# Convert sql database to dataframe
df = pd.read_sql_query("SELECT * FROM messages", connection)
# df = df.rename(
#     columns={
#         "user_id": "User",
#         "msg": "Message",
#         "label": "Sentiment",
#         "msg_type": "MessageType",
#         "date": "Timestamp"
#     }
# )
df['Timestamp'] = pd.to_datetime(df['date'])
df['Date'] = df['Timestamp'].dt.date
df['Time'] = df['Timestamp'].dt.time
# Ajout d'une colonne 'Type' pour distinguer les messages reçus et envoyés
df['Type'] = df.apply(
    lambda row: 'Reçu' if row['user_id'] != 'UtilisateurActuel'
    else 'Envoyé', axis=1
)
# Suppression des messages vides
df = df.dropna()


# Configuration de l'affichage de l'appli
st.set_page_config(
    layout='wide',  # Ajuster la mise en page si nécessaire
    initial_sidebar_state='collapsed',
)

# Obtenir et afficher la dernière date d'actualisation
last_update_date = get_last_update_date()
st.write(f"Dernière actualisation : {last_update_date}")

# App title
st.title('Mon ami Dobby')

# App logo in sidebar
image = Image.open(logo_path)
st.sidebar.image(image, caption="Première appli de détéction de cybrharcèlement", use_column_width=True)

# Sidebar
st.sidebar.header('Navigation')
tabs = st.sidebar.radio("", ["Données du jour", "Historique"])



# Fonction pour filtre
# Filtrer les types de messages uniques pour les options "Tous"
all_msg_types = ['Tous'] + df['msg_type'].unique().tolist()

# Filtrer les sentiments uniques pour les options "Tous"
all_sentiments = ['Tous'] + df['label'].unique().tolist()

# Visualizations for "Données du jour"
if tabs == "Données du jour":
    # Calcul du nombre total de messages par utilisateur
    total_messages_per_user = df.groupby('user_id')['msg'].count().reset_index(name='TotalMessages') # Acorriger

    # Calcul du nombre de messages négatifs par utilisateur
    negative_messages_per_user = df[df['label'] == 'haineux'].groupby('user_id')['msg'].count().reset_index(
        name='NegativeMessages')

    # Fusion des données par utilisateur
    user_data = pd.merge(total_messages_per_user, negative_messages_per_user, on='user_id', how='left').fillna(0)

    # Calcul du pourcentage de négativité par utilisateur
    user_data['NegativityPercentage'] = (user_data['NegativeMessages'] / user_data['TotalMessages']) * 100

    ## Filtre de la page "Donnée du jour"
    st.sidebar.header("Filtre")

    # Sélection de l'utilisateur actuel
    user_options = ['Tous les utilisateurs'] + df['user_id'].unique().tolist()
    selected_user = st.sidebar.selectbox("Sélectionnez un utilisateur", user_options)

    # Récupération du pourcentage de négativité pour l'utilisateur sélectionné
    selected_user_data = user_data[user_data['user_id'] == selected_user]
    
    if not selected_user_data.empty:
        negativity_percentage = selected_user_data['NegativityPercentage'].values[0]
    else:
        negativity_percentage = 0

    #### Calculs de filtre
    if selected_user == 'Tous les utilisateurs':
        filtered_df_today = df[df['Timestamp'].dt.date == datetime.now().date()]
    else:
        filtered_df_today = df[(df['Timestamp'].dt.date == datetime.now().date()) & (df['user_id'] == selected_user)]

    nombre_messages_positifs = filtered_df_today['label'].value_counts().get('non haineux', 0)
    nombre_messages_negatifs = filtered_df_today['label'].value_counts().get('haineux', 0)        
    nombre_messages_text_today = filtered_df_today['msg_type'].value_counts().get('text', 0)
    nombre_messages_vocal_today = filtered_df_today['msg_type'].value_counts().get('vocal', 0)

    # Calcul du pourcentage (prenant en compte l'absence de message)
    if len(filtered_df_today) > 0:
        pourcent_messages_text_today = (nombre_messages_text_today / len(filtered_df_today)) * 100
        pourcent_messages_vocal_today = (nombre_messages_vocal_today / len(filtered_df_today)) * 100
    else:
        pourcent_messages_text_today = 0
        pourcent_messages_vocal_today = 0

    indice1, indice2, indice3, indice4 = st.columns(4, gap='large')

    # Redimensionnement des images
    resized_image_indice1 = resize_image(I1_path)
    resized_image_indice2 = resize_image(I2_path)
    resized_image_indice3 = resize_image(I3_path)
    resized_image_indice4 = resize_image(I4_path)

    # Nombre d'utilisateur
    with indice1:
        st.image(resized_image_indice1, use_column_width='Auto')
        st.metric(label="Total de message", value=len(filtered_df_today))

    with indice2:
        st.image(resized_image_indice2, use_column_width='Auto')
        st.metric(label="Messages normaux", value=nombre_messages_positifs)

    with indice3:
        st.image(resized_image_indice3, use_column_width='Auto')
        st.metric(label="Messages Haineux", value=nombre_messages_negatifs)

    with indice4:
        negativity_percentage = calculate_negativity_level(filtered_df_today)
        st.image(resized_image_indice4, use_column_width='Auto')
        st.metric(label="Taux de négativité", value=f"{negativity_percentage:.2f}%")

    # Création du pie chart et de la jauge
    header_left, header_mid, header_right = st.columns([6, 1, 1], gap='large')
    with header_left:
        st.header("Suivie de l'activité journalière")

    Q1, Q2 = st.columns(2, gap='large')  # on peut ajouter un Q3

    with Q1:
        # Pie chart for message types
        st.markdown("Type de messages échangés")
        pie_data_today = pd.DataFrame({'Type de Message': ['Text', 'Vocal'], 'Pourcentage': [pourcent_messages_text_today, pourcent_messages_vocal_today]})
        st.plotly_chart(px.pie(pie_data_today, names='Type de Message', values='Pourcentage'), use_container_width=True)

    with Q2:
        # Création de la jauge
        st.markdown("Jauge de négativité")
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=negativity_percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgreen"},
                        {'range': [25, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}
                }
            )
        )
        # Affichage de la jauge
        st.plotly_chart(fig, title="Niveau de négativité", use_container_width=True)

    # Display messages of the day
    st.subheader('Messagerie du jour')
    st.dataframe(filtered_df_today)

# Visualizations for "Historique"
elif tabs == "Historique":
    # Filtres
    st.sidebar.header("Filtres")
    start_date_hist = st.sidebar.date_input("Date de début", min_value=df['Date'].min(), max_value=df['Date'].max(),
                                            value=df['Date'].min())
    end_date_hist = st.sidebar.date_input("Date de fin", min_value=df['Date'].min(), max_value=df['Date'].max(),
                                          value=df['Date'].max())
    sentiment_filter = st.sidebar.selectbox("Filtrer par sentiment", all_sentiments)
    message_type_filter = st.sidebar.selectbox("Filtrer par type de message", all_msg_types)
    time_granularity_hist = st.sidebar.selectbox("Granularité temporelle", ['Par jour', 'Par mois', 'Par année'])
    users_filter = st.sidebar.selectbox("Filtrer par utilisateur", ['Tous les utilisateurs'] + df['user_id'].unique().tolist())

    # Convertir les valeurs en datetime64
    start_date_hist = np.datetime64(start_date_hist)
    end_date_hist = np.datetime64(end_date_hist)

    # Filtrage du DataFrame
    if users_filter == 'Tous les utilisateurs':
        filtered_df_hist = df[
            (df['Date'] >= start_date_hist) &
            (df['Date'] <= end_date_hist) &
            ((sentiment_filter == 'Tous') | (df['label'] == sentiment_filter)) &
            ((message_type_filter == 'Tous') | (df['msg_type'] == message_type_filter))
        ]
    else:
        filtered_df_hist = df[
            (df['Date'] >= start_date_hist) &
            (df['Date'] <= end_date_hist) &
            ((sentiment_filter == 'Tous') | (df['label'] == sentiment_filter)) &
            ((message_type_filter == 'Tous') | (df['msg_type'] == message_type_filter))&
        (df['user_id'] == users_filter)
        ]

    # Statistiques
    st.subheader('Statistiques Historique')

    H1, H2, H3, H4 = st.columns(4, gap='large')

    nombre_messages_positifs_hist = filtered_df_hist['label'].value_counts().get('non haineux', 0)
    nombre_messages_negatifs_hist = filtered_df_hist['label'].value_counts().get('haineux', 0)
    nombre_messages_text_hist = filtered_df_hist['msg_type'].value_counts().get('text', 0)
    nombre_messages_vocal_hist = filtered_df_hist['msg_type'].value_counts().get('vocal', 0)
    pourcent_messages_text_hist = (nombre_messages_text_hist / len(filtered_df_hist)) * 100 if len(filtered_df_hist) != 0 else 0
    pourcent_messages_vocal_hist = (nombre_messages_vocal_hist / len(filtered_df_hist)) * 100 if len(filtered_df_hist) != 0 else 0

    # Redimensionner les images
    resized_image_H1 = resize_image(H1_path)
    resized_image_H2 = resize_image(H2_path)
    resized_image_H3 = resize_image(H3_path)
    resized_image_H4 = resize_image(H4_path)

    with H1:
        st.image(resized_image_H1, use_column_width='Auto')
        st.metric(label="Nombre total de messages", value=len(filtered_df_hist))

    with H2:
        st.image(resized_image_H2, use_column_width='Auto')
        st.metric(label="Nombre de messages positifs", value=nombre_messages_positifs_hist)

    with H3:
        st.image(resized_image_H3, use_column_width='Auto')
        st.metric(label="Nombre de messages négatifs", value=nombre_messages_negatifs_hist)
    
    with H4:
        negativity_percentage = calculate_negativity_level(filtered_df_hist)
        st.image(resized_image_H4, use_column_width='Auto')
        st.metric(label="Taux de négativité", value=f"{negativity_percentage:.2f}%")

    Q4, Q5 = st.columns([1, 2], gap='large')

    # Pie chart pour les types de messages
    with Q4:
        st.subheader("Répartition des messages par types")
        pie_data_hist = pd.DataFrame({'Type de Message': ['Text', 'Vocal'], 'Pourcentage': [pourcent_messages_text_hist, pourcent_messages_vocal_hist]})
        st.plotly_chart(px.pie(pie_data_hist, names='Type de Message', values='Pourcentage'))

    # Graphique temporel
    with Q5:
        st.subheader("Analyse des messageries au cours du temps")
        if time_granularity_hist == 'Par jour':
            grouped_data_hist = filtered_df_hist.groupby(['label', pd.Grouper(key='Timestamp', freq='D')]).size().reset_index(
                name='Count')

        elif time_granularity_hist == 'Par mois':
            grouped_data_hist = filtered_df_hist.groupby(['label', pd.Grouper(key='Timestamp', freq='M')]).size().reset_index(
                name='Count')
        else:  # Par année par défaut
            grouped_data_hist = filtered_df_hist.groupby(['label', pd.Grouper(key='Timestamp', freq='Y')]).size().reset_index(
                name='Count')

        # Création du graphique
        fig_hist = px.line(grouped_data_hist, x='Timestamp', y='Count', color='label', markers=True,
                           line_dash="label",
                           # title='Analyse des messageries au cours du temps',
                           labels={'Count': 'Nombre de Messages', 'Timestamp': 'Date'})

        # Affichage du graphique
        st.plotly_chart(fig_hist, use_container_width=True)

    ### Display messages of the historique
    st.subheader('Historique des messages')
    st.dataframe(filtered_df_hist)


# Détection des tilisateurs les plus suspects ayant envoyés plus de 15 messages haineux en 24h de temps
# Filtre  DataFrame pour inclure uniquement les messages haineux
df_haineux = df[df['label'] == 'haineux']

# Identification les utilisateurs ayant envoyé plus de 15 messages haineux
users_with_high_negativity = df_haineux['user_id'].value_counts()[df_haineux['user_id'].value_counts() > THRESHOLD].index.tolist()

# Yoel
start_date_hist = st.sidebar.date_input("Date de début", min_value=df['Date'].min(), max_value=df['Date'].max(),
                                            value=df['Date'].min(), key="sd")
end_date_hist = st.sidebar.date_input("Date de fin", min_value=df['Date'].min(), max_value=df['Date'].max(),
                                        value=df['Date'].max(), key="ed")
# Convertir les valeurs en datetime64
start_date_hist = np.datetime64(start_date_hist)
end_date_hist = np.datetime64(end_date_hist)

# Filtrer le DataFrame pour inclure uniquement ces utilisateurs dans une plage de dates spécifique
filtered_df_toxic_user = df[df['user_id'].isin(users_with_high_negativity) &
                            (df['Date'] >= start_date_hist) &
                            (df['Date'] <= end_date_hist)]

# Calcule du  taux de négativité pour chaque utilisateur
negativity_rates = filtered_df_toxic_user.groupby('user_id').apply(calculate_negativity_level)

# graphique à barres des personnes les plus toxiques
st.subheader('Utilisateurs suspects')
st.bar_chart(negativity_rates)
