# -*- coding: utf-8 -*-
import os
import io
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import speech_recognition
from pydub import AudioSegment
from discord import Intents, Client
from discord.message import Message

from MAD.model import MAD_Classifier
from MAD.database import MAD_Database


def audio_to_text(attachement) -> str:
    tmp_file = os.path.join(
        "data/audio",
        attachement.filename.replace("ogg", "flac")
    )
    
    # URL Request
    request = Request(
        attachement.url, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    # Open URL
    try:
        response = urlopen(request)
    except HTTPError as e:
        print('Error code: ', e.code)
        return "Erreur de conversion"
    except URLError as e:
        print('Reason: ', e.reason)
        return "Erreur de conversion"

    # Read URL and convert to io
    audio_io = io.BytesIO(response.read())
    # Read audio from OGG format
    audio_ogg = AudioSegment.from_ogg(audio_io)
    # Convert audio to FLAC format & save to temporary file
    audio_ogg.export(tmp_file, format='flac')

    # Read audio file
    audio_file = speech_recognition.AudioFile(tmp_file)
    # initialize the recognizer
    r = speech_recognition.Recognizer()
    # Extracting the audio & removing ambient noice
    with audio_file as source:
        r.adjust_for_ambient_noise(source)
        audio = r.record(source)
    # Recognize the audio
    try:
        text =  r.recognize_google(audio, language="fr-FR")
    except Exception as e:
        print(e)
        return "Erreur de conversion"

    return text


class MAD_Bot(Client):
    """
    Discord Bot to classify messages in a channel as
    hateful or non hateful and store them in a database
    """
    def __init__(
            self,
            intents: Intents,
            database: MAD_Database,
            classifier: MAD_Classifier
    ) -> None:
        super().__init__(intents=intents)
        self.db = database
        self.classifier = classifier
    
    callbacks = []
    def add_callback(self, callback):
        self.callbacks.append(callback)

    async def on_ready(self):
        print(f"Connecté à Discord en tant que {self.user}!")
        for guild in self.guilds:
            # On récupère tous les channels de texte
            for channel in guild.text_channels:
                if channel.name in ["rules", "moderator-only"]:
                    continue
                self.db.cursor.execute(
                    """
                    INSERT INTO channels(channel_id, name, num_users)
                    VALUES ('{id}', ?, {num_users})
                    ON CONFLICT(channel_id) DO UPDATE SET
                        name = ?,
                        num_users = {num_users}
                    """
                    .format(
                        id=channel.id,
                        num_users=len(channel.members)
                    ),
                    [channel.name, channel.name]
                )
                self.db.connexion.commit()

                # On récupère tous les messages du channel
                messages = channel.history(limit=None, oldest_first=False)
                async for msg in messages:
                    msg_type = "text"
                    if msg.attachments:
                        for att in msg.attachments:
                            if "voice-message" in att.filename:
                                # Recognize the audio
                                msg.content = audio_to_text(att)
                                msg_type = "audio"

                    # On refait une prédiction sur chaque ancien message au cas où on change de modèle
                    pred = self.classifier.predict(msg.content)[0]
                    pred["label"] = "haineux" if pred["label"] == "LABEL_1" else "non haineux"
                    self.db.insert_message(msg, msg_type, pred)

                self.db.connexion.commit()
        
    async def on_message(self, msg: Message):
        msg_type = "text"
        if msg.attachments:
            for att in msg.attachments:
                if "voice-message" in att.filename:
                    # Recognize the audio
                    msg.content = audio_to_text(att)
                    msg_type = "audio"

        pred = self.classifier.predict(msg.content)[0]
        pred["label"] = "haineux" if pred["label"] == "LABEL_1" else "non haineux"
        self.db.insert_message(msg, msg_type, pred)
        self.db.connexion.commit()