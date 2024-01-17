# -*- coding: utf-8 -*-
from transformers import TextClassificationPipeline
from transformers import CamembertTokenizer, CamembertForSequenceClassification

from .utils import clean_text

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
        # Ensure proper string format of text
        instances = [clean_text(str(t)) for t in text]
        try:
            predictions = self.pipeline(instances)
            for pred in predictions:
                if pred["label"] == "LABEL_1":
                    pred["label"] = "haineux"
                else:
                    pred["label"] = "non haineux"
        except Exception as e:
            print(f"Classification error due to : {e}")
            return [{'label': 'Non clasifié', 'score': 1.0}]
        
        return predictions
