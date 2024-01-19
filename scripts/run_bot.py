# -*- coding: utf-8 -*-
import os
import logging

import discord
from pydub import AudioSegment
from dotenv import load_dotenv

from MAD.bot import MAD_Bot
from MAD.model import MAD_Classifier
from MAD.database import MAD_Database

# Set environment variables
load_dotenv()
FS_ROOT = os.path.abspath(os.sep)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_FILE = os.getenv("DATABASE_FILE")
MODEL_DIR = os.getenv("MODEL_DIR")

# Set ffmpeg bin
AudioSegment.converter = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffmpeg.exe")
AudioSegment.ffmpeg = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffprobe.exe")

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