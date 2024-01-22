# -*- coding: utf-8 -*-
import sys
import logging
sys.path.insert(0, './src')

import discord

from MAD.bot import MAD_Bot
from MAD.model import MAD_Classifier
from MAD.database import MAD_Database
from MAD import DISCORD_TOKEN, DATABASE_FILE, MODEL_DIR

if __name__ == "__main__":
    handler = logging.FileHandler(
        filename='logs/discord.log',
        encoding='utf-8',
        mode='w'
    )
    
    classifier = MAD_Classifier(MODEL_DIR)
    db = MAD_Database(DATABASE_FILE)
    db.initialize_database()

    intents = discord.Intents.default()
    intents.message_content = True
    client = MAD_Bot(intents, db, classifier)
    client.run(
        token=DISCORD_TOKEN,
        log_handler=handler,
        log_level=logging.DEBUG
    )