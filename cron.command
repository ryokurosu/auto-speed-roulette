#!/bin/sh

killall python
killall chromedriver
killall chrome

# export DISPLAY=:0
PROG_DIR=`dirname $0`

cd $PROG_DIR
git pull origin master

source $PROG_DIR/env/bin/activate
pip3 install -r requirements.txt
nohup python3 $PROG_DIR/cron.py > $PROG_DIR/logs/`date +%Y%m%d_%H%M%S`.log &