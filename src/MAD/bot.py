# -*- coding: utf-8 -*-
import discord
from discord import Intents

from MAD.model import MAD_Classifier
from MAD.database import MAD_Database

class MAD_Bot(discord.Client):
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
                    # On refait une prédiction sur chaque ancien message au cas où on change de modèle
                    pred = self.classifier.predict(msg.content)[0]
                    pred["label"] = "hateful" if pred["label"] == "LABEL_1" else "non-hateful"
                    self.db.insert_message(msg, pred)
                self.db.connexion.commit()
        
    async def on_message(self, msg):
        pred = self.classifier.predict(msg.content)[0]
        pred["label"] = "hateful" if pred["label"] == "LABEL_1" else "non-hateful"
        self.db.insert_message(msg, pred)
        self.db.connexion.commit()