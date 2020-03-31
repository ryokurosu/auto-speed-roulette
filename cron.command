#!/bin/sh

# export DISPLAY=:0
PROG_DIR=`dirname $0`

cd $PROG_DIR
source $PROG_DIR/env/bin/activate
python3 $PROG_DIR/cron.py