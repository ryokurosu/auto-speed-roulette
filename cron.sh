#!/bin/sh

PROG_DIR=/home/root/app
source $PROG_DIR/env/bin/activate

python $PROG_DIR/cron.py
