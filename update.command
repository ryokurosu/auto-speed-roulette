#!/bin/sh

PROG_DIR=`dirname $0`

cd $PROG_DIR

git fetch
git reset --hard origin/master
rm chromedriver
wget -P $PROG_DIR https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_mac64.zip
unzip chromedriver_mac64.zip
rm chromedriver_mac64.zip
rm -rf env
python3 -m venv env
source $PROG_DIR/env/bin/activate
pip3 install -r requirements.txt
rm -rf logs
mkdir logs
