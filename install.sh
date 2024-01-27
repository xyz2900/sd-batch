#!/bin/sh  
apt -y install python3.10
apt -y install libpython3.10-dev
apt -y install build-essential
apt -y install ffmpeg
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 torchtext==0.15.2 torchdata==0.6.1 --extra-index-url https://download.pytorch.org/whl/cu118 -U
python3.10 -m pip install xformers==0.0.20 triton==2.0.0 -U
python3.10 -m pip install httpx==0.24.1
python3.10 -m pip install insightface -U
python3.10 -m pip install matplotlib -U
python3.10 -m pip install ipython -U
