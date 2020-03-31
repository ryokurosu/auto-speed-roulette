#!/bin/sh

PROG_DIR=`dirname $0`

cd $PROG_DIR

git fetch
git reset --hard origin/master

mkdir logs
source $PROG_DIR/env/bin/activate
pip3 install -r requirements.txt