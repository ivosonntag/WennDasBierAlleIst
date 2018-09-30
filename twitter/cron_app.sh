#!/usr/bin/env bash

working_dir="/home/fabian/repo/WennDasBierAlleIst/"

cd ${working_dir}
source .env/bin/activate
cd twitter/
source credentials.txt
python deletion_checker.py
