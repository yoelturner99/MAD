# -*- coding: utf-8 -*-
import io
import tempfile
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import speech_recognition
from pydub import AudioSegment
from discord import Intents, Client
from discord.message import Message, Attachment

from .model import MAD_Classifier
from .database import MAD_Database


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

    def audio_to_text(self, attachement: Attachment) -> str:       
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

        # Create temporary file
        fd, tmp_path = tempfile.mkstemp(suffix=".flac")
        # Convert audio to FLAC format & save in tmpfile
        audio_ogg.export(tmp_path, format='flac')
        # Read audio file
        audio_file = speech_recognition.AudioFile(tmp_path)
        
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
                            if att.is_voice_message():
                                # Recognize the audio
                                msg.content = self.audio_to_text(att)
                                msg_type = "vocal"

                    # On refait une prédiction sur chaque ancien message au cas où on change de modèle
                    pred = self.classifier.predict(msg.content)[0]
                    self.db.insert_message(
                        msg=msg,
                        msg_type=msg_type,
                        pred=pred
                    )

                self.db.connexion.commit()
        print("Database updated !!!")
        
    async def on_message(self, msg: Message):
        msg_type = "text"
        if msg.attachments:
            for att in msg.attachments:
                if att.is_voice_message():
                    # Recognize the audio
                    msg.content = self.audio_to_text(att)
                    msg_type = "vocal"

        pred = self.classifier.predict(msg.content)[0]
        self.db.insert_message(
            msg=msg,
            msg_type=msg_type,
            pred=pred
        )
        self.db.connexion.commit()