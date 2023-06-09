#!/usr/bin/bash

rm -rf .venv/ __pycache__/ build/ dist/ myPRL-qt.spec
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m PyInstaller myPRL-qt.py
deactivate