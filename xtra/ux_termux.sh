#!/bin/bash

### by Ryuk ###

clear

echo -e "\nInstalling required packages for Bot
this may take a while."
echo -e "\n*** Spam incoming in 5 ***"

sleep 6

yes|apt install \
    apt-utils curl git gnupg2 wget unzip tree gcc zlib1g-dev neofetch \
    apt-transport-https build-essential coreutils jq pv ffmpeg mediainfo \
    libfreetype6-dev libjpeg-dev libpng-dev libgif-dev libwebp-dev p7zip-full \
    python3 python-dev-is-python3 python3-distutils libxslt-dev libxml2 nano python3-pip

pip -q install -U pip wheel setuptools

clear

echo -e "\nClonning Repo."

git clone -q https://github.com/ux-termux/ux ~/ux

cd ~/ux

echo -e "\nDone, Now Installing requirements,
this may take a while, wait patiently."

pip install --no-cache-dir -r reqs.txt

clear

echo -e "\nFollow the next step in guide."


