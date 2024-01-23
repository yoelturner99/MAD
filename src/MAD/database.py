# -*- coding: utf-8 -*-
import sqlite3
from discord.message import Message

from . import logger
from .utils import clean_text

class MAD_Database():
    """An SQLite3 database to insert all messages in the channels 
    along with their corresponding labels (hateful or non-hateful)
    Schema of messages table:\n
    msg_id | channel_id	| user_id | msg | msg_type |label | score | date

    Schema of channels table:\n
    channel_id | name | num_users
    """
    def __init__(self, database_file):
        self.connexion = sqlite3.connect(database_file)
        self.cursor = self.connexion.cursor()
    
    def initialize_database(self):
        rep = self.cursor.execute(
            """
            SELECT count(*) FROM sqlite_master
            WHERE type='table' AND name='channels'
            """
        ).fetchone()

        if rep[0] == 0:
            self.cursor.execute(
                """
                CREATE TABLE channels(
                    channel_id TEXT PRIMARY KEY NOT NULL, 
                    name TEXT, 
                    num_users INTEGER
                )
                """
            )
            self.cursor.execute(
                """
                CREATE TABLE messages(
                    msg_id TEXT PRIMARY KEY NOT NULL,
                    channel_id TEXT NOT NULL,
                    user_id TEXT,
                    msg TEXT,
                    msg_type TEXT,
                    label TEXT,
                    score DOUBLE,
                    date TEXT
                )
                """
            )
        logger.info("Database initialized !!!")
    
    def insert_message(self, msg: Message, msg_type: str, pred: str):
        """
        Insert new messages and update records of previous messages
        in the database.
        """

        self.cursor.execute(
            """
            INSERT INTO messages(msg_id, channel_id, user_id, msg, msg_type, label, score, date)
            VALUES ('{msg_id}', '{channel_id}', ?, ?, '{msg_type}', '{label}', {score}, '{date}')
            ON CONFLICT(msg_id) DO UPDATE SET
                msg = ?,
                label = '{label}',
                score = {score}
            """
            .format(
                msg_id=msg.id,
                channel_id=msg.channel.id,
                msg_type=msg_type,
                label=pred["label"],
                score=pred["score"],
                date=msg.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            ),
            [str(msg.author), clean_text(str(msg.content)), clean_text(str(msg.content))]
        )
