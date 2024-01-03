# -*- coding: utf-8 -*-
import re
from transformers import TextClassificationPipeline
from transformers import CamembertTokenizer, CamembertForSequenceClassification

class MAD_Classifier():
    """
    CamemBERT pipeline (Model + Tokenizer) to do binary classification
    for hateful (1) and non-hateful (0) statement in french.
    """
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.pipeline = self.load_pipeline()

    def load_pipeline(self):
        # Initializing tokenizer
        tokenizer = CamembertTokenizer.from_pretrained(self.model_dir)
        # Load Model
        model = CamembertForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=self.model_dir, # Use the 12-layer CamemBERT
            # num_labels=num_labels, # Binary classification.
            # output_attentions=False, # Whether the model returns attentions weights.
            # output_hidden_states=False, # Whether the model returns all hidden-states.
        )
        # Building pipeline
        pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)
        return pipeline

    def predict(self, text):
        if isinstance(text, str):
            text = [text]
            
        instances = []
        for t in text:
            # Ensure proper string format of text
            t = str(t).lower() \
                .replace("@user", "") \
                .replace("@url", "")
            t = re.sub(r"[\.,\?\!]", "", t)
            t = re.sub(r"\d*", "", t)
            t = re.sub(r"\s+", " ", t)
            instances.append(t)
            
        predictions = self.pipeline(instances)
        return predictions
