#!/bin/bash

rm -r ${PWD}/.venv

python3 -m venv .venv
while ! test -f "${PWD}/.venv/bin/activate"; do
    echo "waiting for python virtual environment to be created..."
    sleep 1
done
source .venv/bin/activate
echo "changed to virtual environment .venv"
python3 -m pip install --upgrade pip
pip3 install -q nicegui
pip3 install -q psycopg2-binary
pip3 install -q sqlalchemy
pip3 install -q pandas
pip3 install -q tqdm
