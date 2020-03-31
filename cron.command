#!/bin/sh

# export DISPLAY=:0
PROG_DIR=`dirname $0`

cd $PROG_DIR
git fetch origin
git reset --hard origin master

python3 -m venv env
source $PROG_DIR/env/bin/activate
pip3 install -r requirements.txt
python3 $PROG_DIR/cron.py