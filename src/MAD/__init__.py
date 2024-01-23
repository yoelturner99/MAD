# -*- coding: utf-8 -*-

import os
import logging
import platform
from logging.config import fileConfig
from pydub import AudioSegment
from dotenv import load_dotenv

# Set environment variables
load_dotenv()
LOG_CONFIG = os.getenv("LOG_CONFIG")

# Set logger
if not os.path.exists(LOG_CONFIG):
    raise Exception(
        f"Missing logging config file in directory: {LOG_CONFIG}"
    )
fileConfig(fname=LOG_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Set ffmpeg bin
if platform.system() == "Windows":
    AudioSegment.converter = os.popen('where ffmpeg').read().strip("\n")
    AudioSegment.ffmpeg    = os.popen('where ffmpeg').read().strip("\n")
    AudioSegment.ffprobe   = os.popen('where ffprobe').read().strip("\n")
else:
    AudioSegment.converter = os.popen('which ffmpeg').read().strip("\n")
    AudioSegment.ffmpeg    = os.popen('which ffmpeg').read().strip("\n")
    AudioSegment.ffprobe   = os.popen('which ffprobe').read().strip("\n")