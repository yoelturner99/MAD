# -*- coding: utf-8 -*-

import os
import logging
from logging.config import fileConfig
from pydub import AudioSegment
from dotenv import load_dotenv

# Set environment variables
load_dotenv()
FS_ROOT       = os.path.abspath(os.sep)
MODEL_DIR     = os.getenv("MODEL_DIR")
LOG_CONFIG    = os.getenv("LOG_CONFIG")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_FILE = os.getenv("DATABASE_FILE")

# Set logger
if not os.path.exists(LOG_CONFIG):
    raise Exception(
        f"Missing logging config file in directory: {LOG_CONFIG}"
    )
fileConfig(fname=LOG_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger(name="MAD")

# Set ffmpeg bin
AudioSegment.converter = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffmpeg.exe")
AudioSegment.ffmpeg    = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffmpeg.exe")
AudioSegment.ffprobe   = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffprobe.exe")