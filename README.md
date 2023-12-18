# MAD (Mon Ami Dobby)
The aim is to offer an AI capable of identifying situations of cyber-harassment, insults or abusive language. This AI will be integrated into the Discord platform.

## Datasets used from Hugging Face
1) Paul/hatecheck-french
2) hate_speech18 
3) hate_speech_offensive
4) tweets_hate_speech_detection
5) limjiayi/hateful_memes_expanded 
6) classla/FRENK-hate-en 
7) ucberkeley-dlab/measuring-hate-speech 
8) hatexplain

## Environment (python 3.10)
Using python and pip
```bash
# Create venv
python -m venv .venv/Scripts/activate
# Activate venv in terminal
./.venv/Scripts/activate
# Install packages
pip install -r ./requirements.txt
```
Using conda
```bash
# Create conda env and install packages
conda env create --file environment.yml
# Activate conda env
conda activate mad-env
```

To do training and inferences on GPU, download pytorch-cuda version (https://pytorch.org/get-started/previous-versions/) with the following commands in the terminal :
```bash
## To install pytorch-cuda version
pip install torch==1.12.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113
# OR
conda install pytorch==1.12.1 cudatoolkit=11.3 -c pytorch
```

## Scripts
### scripts/finetuning.py
```bash
# To run the training script
python ./scripts/finetuning.py --data_path ./data/text/final/train_data.tsv
```
```bash
# To run tensorboard for monitoring
tensorboard --logdir=runs
```

### scripts/testing.py
```bash
python ./scripts/testing.py --data_path ./data/text/final/test_data.tsv --model_dir ./models/camembert_mad_v1
```