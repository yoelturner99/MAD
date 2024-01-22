# -*- coding: utf-8 -*-
# import sys
# sys.path.insert(0, './src')
import os
import logging
from pathlib import Path

import discord

from MAD.bot import MAD_Bot
from MAD.model import MAD_Classifier
from MAD.database import MAD_Database
from MAD import (
    MODEL_DIR,
    DISCORD_TOKEN,
    DATABASE_FILE,
)

if __name__ == "__main__":
    # Initialize database
    if not os.path.exists(DATABASE_FILE):
        path = Path(DATABASE_FILE)
        os.makedirs(path.parent, exist_ok=True)
        
    db = MAD_Database(DATABASE_FILE)
    db.initialize_database()

    # Initialize Classifier
    classifier = MAD_Classifier(MODEL_DIR)

    # Initialize Client
    intents = discord.Intents.default()
    intents.message_content = True
    client = MAD_Bot(intents, db, classifier)

    # Add handler for logging
    handler = logging.FileHandler(
        filename='logs/discord.log',
        encoding='utf-8',
        mode='w'
    )

    # Run client 
    client.run(
        token=DISCORD_TOKEN,
        log_handler=handler,
        log_level=logging.DEBUG
    )