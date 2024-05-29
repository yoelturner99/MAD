# MAD (Mon Ami Dobby)
The aim is to offer an AI capable of identifying situations of cyber-harassment, insults or abusive language. This AI will be integrated into the Discord platform.

## Venv Installation (python 3.10)
Using python and pip
```bash
# Create venv
python -m venv .venv
# Activate venv in terminal
./.venv/Scripts/activate
# Install packages 
pip install -r ./requirements.txt
# To pull model and data from server
dvc pull
```
Using conda
```bash
# Create conda env and install packages
conda env create --file environment.yml
# Activate conda env
conda activate mad-env
# To pull model and data from server
dvc pull
```
## FFMPEG Installation
**On Windows :** Run `notebooks/01_ffmpeg.ipynb` \
**On Linux :** Run command ```bash apt-get install -y ffmpeg```

## CUDA for PyTorch Installation
To do training and inference on GPU, download pytorch-cuda version (https://pytorch.org/get-started/previous-versions/) with the following commands in the terminal :
```bash
## To install pytorch-cuda version
pip install torch==1.12.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113
# OR
conda install pytorch==1.12.1 cudatoolkit=11.3 -c pytorch
```

## .env file
```python
LOG_CONFIG=./logs/log_config.ini
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_TOKEN=your_discord_bot_token
```

## Scripts
#### scripts/finetuning.py
```bash
# To run the training script
python ./scripts/finetuning.py --data_path ./data/text/final/train_data.tsv --model_name camembert_mad_v0

# To run tensorboard for monitoring
tensorboard --logdir=runs
```

#### scripts/testing.py
```bash
python ./scripts/testing.py --data_path ./data/text/final/test_data.tsv --model_dir ./models/camembert_mad_v1
```

#### scripts/run_bot.py
```bash
python ./scripts/run_bot.py
```

#### scripts/dashboard.py
```bash
streamlit run ./scripts/dashboard.py
```

## Datasets used from Hugging Face
1) Paul/hatecheck-french
2) hate_speech18 
3) hate_speech_offensive
4) tweets_hate_speech_detection
5) limjiayi/hateful_memes_expanded 
6) classla/FRENK-hate-en 
7) ucberkeley-dlab/measuring-hate-speech 
8) hatexplain
