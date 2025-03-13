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
pip3 install nicegui
pip3 install psycopg2-binary
pip3 install sqlalchemy
pip3 install pandas
pip3 install tqdm
