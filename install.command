#!/bin/sh
sudo xcode-select --install
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install python3 git wget
python3 -m pip install --upgrade pip
pip3 install virtualenv

PROG_DIR=`dirname $0`
cd $PROG_DIR

rm -rf env
python3 -m venv env
source $PROG_DIR/env/bin/activate
pip3 install -r requirements.txt

chmod 777 cron.py
chmod 777 cron.command
chmod 777 update.command
