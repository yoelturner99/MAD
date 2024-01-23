# -*- coding: utf-8 -*-

import re

def clean_text(text: str) -> str:
    # text = str(text).lower()
    text = text.replace("@user", "").replace("@url", "")
    text = re.sub(r"[\.,\?\!]", "", text)
    text = re.sub(r"\d*", "", text)
    text = re.sub(r"\s+", " ", text)
    
    return text