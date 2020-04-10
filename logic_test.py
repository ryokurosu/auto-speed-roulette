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
judge.set_default_val(1)

f = open('logic_test.txt', 'r')
line = f.readline()

while line:
	tmp = line.strip()
	l = literal_eval(tmp)
	for x in range(len(l)):
		result_list = l[0:(x+1)]
		slice_list = cron.result_data_slice(result_list)
		if len(slice_list) >= 3:
			judge.run(0,"テスターテーブル",result_list,slice_list)
	
	line = f.readline()
f.close()
judge.test_result()
# judge.exec(i,table_name,result_list,slice_list)
			