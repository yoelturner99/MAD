# -*- coding: utf-8 -*-
import os
from pydub import AudioSegment
from dotenv import load_dotenv

# Set environment variables
load_dotenv()
FS_ROOT       = os.path.abspath(os.sep)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_FILE = os.getenv("DATABASE_FILE")
MODEL_DIR     = os.getenv("MODEL_DIR")

# Set ffmpeg bin
AudioSegment.converter = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffmpeg.exe")
AudioSegment.ffmpeg    = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffmpeg.exe")
AudioSegment.ffprobe   = os.path.join(FS_ROOT, "ffmpeg", "bin", "ffprobe.exe")