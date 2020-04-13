#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import urllib.parse
import time
import random
from datetime import datetime, timedelta, timezone
import re
import math
import os
import sys
import judge
import message
import cron
import traceback
import fractions
import subprocess
import copy
from ast import literal_eval



message.set_debug()
f = open('logic_test.txt', 'r')
line = f.readline()

while line:
	tmp = line.strip()
	l = literal_eval(tmp)
	number_logs = tuple([])
	judge.set_default_value()
	for x in range(len(l) - 1,-1,-1):
		number_logs = tuple(l[x]) + number_logs
		judge.run(number_logs)
	
	line = f.readline()
f.close()
judge.test_result()
			