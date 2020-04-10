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
import message
import judge
import traceback
import fractions
import subprocess
from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException 
import copy

JST = timezone(timedelta(hours=+9), 'JST')
version = "1.1.0"
array_size = 6
dataset_x = 40
dataset_y = 6

browser = ""
tables = []

start_time = datetime.now(JST)
start = time.time()
loopcount = 0

username = message.username
password = message.password
startURL = "https://www.verajohn.com/ja/livecasino"
liveURL = "https://www.verajohn.com/ja/game/baccarat-lobby-paris"

sp = judge.sp
sb = judge.sb
st = judge.st

none_list = [[None] * dataset_y for k in range(dataset_x)]

# use_tables = ["バカラ A","バカラ B","バカラ C","バカラスクイーズ","バカラコントロールスクイーズ"]
use_tables = ["スピードバカラ A","スピードバカラ B","スピードバカラ C","バカラ A","バカラ B","バカラ C","バカラスクイーズ","バカラコントロールスクイーズ"]


def login():
	browser.get(startURL)
	time.sleep(1)
	browser.implicitly_wait(10)
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'signin-mail'))).send_keys(username)
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'signin-pass'))).send_keys(password)
	time.sleep(1)
	browser.find_element_by_id('edit-submit-signin--2').click()
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.link.link--alone.js-logout')))
	go_to_live()

def go_to_live():
	browser.get(liveURL)
	time.sleep(15)
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gamelayerGameHolder-holder.lazyFrame.loaded')))
	browser.switch_to.frame(browser.find_element_by_css_selector('.gamelayerGameHolder-holder.lazyFrame.loaded'))
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'game-wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('game-wrapper'))
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'evolution_wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('evolution_wrapper'))
	browser.implicitly_wait(1)

def start_browser():
	global browser
	global start_time
	if browser != "":
		browser.quit()
	message_text = "\nTYPE VERA Ver." + version + "\n起動しました。\n" + datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")
	start_time = datetime.now(JST)
	message.send_debug_message(message_text)
	base = os.path.dirname(os.path.abspath(__file__))
	options = webdriver.ChromeOptions()
	options.add_argument('--no-sandbox')
	options.add_argument('--lang=ja-JP')
	options.add_argument('--incognito')

	if os.name == 'nt':
		browser = webdriver.Chrome(os.path.normpath(os.path.join(base, "./chromedriver.exe")),options=options)
	else:
		browser = webdriver.Chrome(os.path.normpath(os.path.join(base, "./chromedriver")),options=options)
	# browser.maximize_window()
	browser.set_window_size(1920,1440)
	login()

def clear_global_key():
	global road_item_colors
	road_item_colors = ""
	global svgs
	svgs = ""

def check_table_name(table_name):
	return table_name in use_tables

def from_dataset_to_result(dataset):
	x = 0
	y = 0
	now_column = 0
	result = ()
	while(True):
		# get data (list)
		d = dataset[x][y]
		if d == None:
			break

		value = d[0]
		# result.extend(d)
		result = result + d

		if y <= (dataset_y - 2) and dataset[x][y + 1] != None and value == dataset[x][y + 1][0]:
			y = y + 1
		elif x <= (dataset_x - 2) and dataset[x + 1][y] != None and value == dataset[x + 1][y][0]:
			x = x + 1
		else:
			now_column = now_column + 1
			x = now_column
			y = 0

	return result 

def result_data_slice(result_list):
	slice_list = []
	columns_count = math.ceil(len(result_list) / array_size)
	for x in range(0,columns_count):
		start = x * array_size
		end = ( x + 1 ) * array_size
		slice_list.append(result_list[start:end])
		pass
	return slice_list

def initialize():
	WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-game="baccarat"]')))
	tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')
	judge.set_default_val(len(tables))

def print_varsize():
    import types
    print("{}{: >15}{}{: >10}{}".format('|','Variable Name','|','  Size','|'))
    print(" -------------------------- ")
    for k, v in globals().items():
        if hasattr(v, 'size') and not k.startswith('_') and not isinstance(v,types.ModuleType):
            print("{}{: >15}{}{: >10}{}".format('|',k,'|',str(v.size),'|'))
        elif hasattr(v, '__len__') and not k.startswith('_') and not isinstance(v,types.ModuleType):
            print("{}{: >15}{}{: >10}{}".format('|',k,'|',str(len(v)),'|'))

if __name__ == "__main__":
	start_browser()
	print(use_tables)
	initialize()

	while(True):
		loopcount = loopcount + 1
		judge.logger.debug("Loop Count : " + str(loopcount))
		time.sleep(0.8)

		signindivs = browser.find_elements_by_css_selector('#signin-mail')
		if len(signindivs) > 0:
			login()
			initialize()
			continue

		if judge.is_betting.count(True) == 0 and (time.time() - start) > 1200:
			go_to_live()
			initialize()
			start = time.time()
			continue

		tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')

		for i in range(len(tables)):
			try:
				table = tables[i]
				tmp = table.text.split("\n")
				table_name = tmp[-3]
				if not table_name or not check_table_name(table_name):
					continue

				road_item_colors = table.find_elements_by_css_selector('g[data-type="roadItemColor"]')
				tmp_tuple = tuple([len(road_item_colors)]) + tuple(tmp[1:-3])

				if judge.check_prev_count(i,tmp_tuple):
					continue

				svgs = table.find_elements_by_css_selector('svg[data-role="Big-road"] svg[data-type="coordinates"]')
				dataset = copy.deepcopy(none_list)

				for svg in svgs:
					additem = ()
					child_svg = svg.find_element_by_css_selector('svg[data-type="roadItem"]')
					name = child_svg.get_attribute('name')
					spl = name.split(' ')
					# additem.append(spl[0])
					v = spl[0][0]
					if v == sp or v == sb or v == st:
						additem = additem + tuple([v])

					if len(spl) > 1 and judge.st in spl[1]:
						if child_svg.text == '':
							additem = additem + tuple([judge.st])
						else:
							additem = additem + tuple([judge.st] * int(child_svg.text))

					dataset[int(svg.get_attribute('data-x'))][int(svg.get_attribute('data-y'))] = additem

				result_list = from_dataset_to_result(dataset)
				slice_list = result_data_slice(result_list)
				judge.exec(i,table_name,result_list,slice_list)
				# print_varsize()
				clear_global_key()

			except Exception as e:
				print(traceback.format_exc())
				pass
			else:
				pass
			finally:
				pass

	browser.quit()
	sys.exit()