# -*- coding: utf-8 -*-
import os

import discord
from pydub import AudioSegment
from dotenv import load_dotenv

from MAD.bot import MAD_Bot
from MAD.model import MAD_Classifier
from MAD.database import MAD_Database

# Set environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_FILE = os.getenv("DATABASE_FILE")
MODEL_DIR = os.getenv("MODEL_DIR")
FFMPEG_BIN = os.getenv("FFMPEG_BIN")

# Set ffmpeg bin
AudioSegment.converter = f"{FFMPEG_BIN}/ffmpeg.exe"
AudioSegment.ffmpeg = f"{FFMPEG_BIN}/ffmpeg.exe"
AudioSegment.ffprobe = f"{FFMPEG_BIN}/ffprobe.exe"

if __name__ == "__main__":
    classifier = MAD_Classifier(MODEL_DIR)
    db = MAD_Database(DATABASE_FILE)
    db.initialize_database()

    intents = discord.Intents.default()
    intents.message_content = True
    client = MAD_Bot(intents, db, classifier)
    client.run(token=DISCORD_TOKEN)