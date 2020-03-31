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
import datetime
import re
import math
import os
import sys
import message
import traceback
import fractions
import subprocess
from dotenv import load_dotenv
from logging import getLogger, StreamHandler, DEBUG, FileHandler, Formatter
from selenium.common.exceptions import NoSuchElementException 


nowdate = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
logger = getLogger(__name__)
handler = StreamHandler()
handler = FileHandler(filename="./logs/" + nowdate + ".log", encoding="utf-8")
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("-----------------------\n%(asctime)s %(message)s\n"))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

version = "1.0.1"
array_size = 6
dataset_x = 40
dataset_y = 6

browser = ""
is_betting = []
prev_count = []
bet_type = []
start_time = datetime.datetime.now()
start = time.time()
loopcount = 0

username = message.username
password = message.password
startURL = "https://www.verajohn.com/ja/livecasino"
liveURL = "https://www.verajohn.com/ja/game/baccarat-lobby-paris"
sp = 'Player'
sb = 'Banker'
st = 'Tie'
type_normal = 'normal'
type_mirror = 'mirror'
use_tables = ["手数料なしバカラ","バカラ A","バカラ B","スピードバカラ A","スピードバカラ B","スピードバカラ C","バカラスクイーズ","バカラコントロールスクイーズ","ライトニングバカラ"]

total_games = 0
win_games = 0

def login():
	logger_set()
	browser.get(startURL)
	time.sleep(1)
	browser.implicitly_wait(10)
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'signin-mail'))).send_keys(username)
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'signin-pass'))).send_keys(password)
	# browser.find_element_by_id('signin-mail').send_keys(username)
	# browser.find_element_by_id('signin-pass').send_keys(password)
	time.sleep(1)
	browser.find_element_by_id('edit-submit-signin--2').click()
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.link.link--alone.js-logout')))
	go_to_live()

def go_to_live():
	browser.get(liveURL)
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gamelayerGameHolder-holder.lazyFrame.loaded')))
	browser.switch_to.frame(browser.find_element_by_css_selector('.gamelayerGameHolder-holder.lazyFrame.loaded'))
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'game-wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('game-wrapper'))
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'evolution_wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('evolution_wrapper'))
	browser.implicitly_wait(1)


def logger_set():
	global logger
	for h in logger.handlers:
		logger.removeHandler(h)
	nowdate = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
	logger = getLogger(__name__)
	handler = StreamHandler()
	handler = FileHandler(filename="./logs/" + nowdate + ".log")
	handler.setLevel(DEBUG)
	handler.setFormatter(Formatter("-----------------------\n%(asctime)s %(levelname)8s %(message)s"))
	logger.setLevel(DEBUG)
	logger.addHandler(handler)
	logger.propagate = False
	return logger


def notice_check(data):
	now = data[-1]
	last = data[-2]
	if now[0] == st:
		return False
	elif now[0] == last[0]:
		return type_normal
	elif now[0] == last[-1]:
		return type_mirror

def check_is_normal(data):
	now = data[-1]
	last = data[-2]
	if now[0] != last[0] or now[1] != last[1]:
		return False

	for x in range(2,len(now)):
		if now[x] != last[x]:
			return False

	return True

def check_is_mirror(data):
	now = data[-1]
	last = data[-2]
	if now[0] != last[-1] or now[1] != last[-2]:
		return False

	for x in range(2,len(now)):
		if now[x] == last[x - 2]:
			return False

	return True

def notice_message(table_name):
	message_text = datetime.datetime.today().strftime("%H:%M ") + table_name + " べット準備してください。"
	logger.debug(message_text)
	message.send_all_message(message_text)

def wait_message(table_name):
	message_text = datetime.datetime.today().strftime("%H:%M ") + table_name + " ベットせずLOOKしてください。"
	logger.debug(message_text)
	message.send_all_message(message_text)

def bet_message(table_name,bet_position):
	message_text = datetime.datetime.today().strftime("%H:%M ") + table_name + " " + bet_position
	logger.debug(message_text)
	message.send_all_message(message_text)

def win_message(table_name):
	message_text = datetime.datetime.today().strftime("%H:%M ") + table_name + " 勝ち（" + str(total_games) + "戦" + str(win_games) + "勝中）" 
	logger.debug(message_text)
	message.send_all_message(message_text)

def start_browser():
	global browser
	global start_time
	if browser != "":
		browser.quit()
	message_text = "起動しました\nONESTEP Vera Ver." + version + "\n" + datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
	start_time = datetime.datetime.now()
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
	browser.maximize_window()
	login()


def clear_global_key():
	global roads
	roads = "cleared"

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

def is_skip(result_list,slice_list):

	if len(slice_list) <= 1:
		#1列目である
		return True

	if len(result_list) > 60:
		#60ゲーム以上
		return True

	now = slice_list[-1]
	last = slice_list[-2]

	if last.count(st) > 0:
		#前列がタイ
		return True
	
	if result_list.count(st) - now.count(st) >= 4:
		#タイが4つ以上
		return True
	
	if now[:3].count(st) > 0:
		#1~3つめにタイ
		return True

	check = True
	for x in range(1,5):
		if last[x] != st and last[x] == last[x - 1] and last[x] == last[x + 1]:
			check = False
		else:
			pass
	return check

start_browser()
print(use_tables)

WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-game="baccarat"]')))
tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')
is_betting = [False] * len(tables)
prev_count = [0] * len(tables)
bet_type = [type_normal] * len(tables)

while(True):
	clear_global_key()
	loopcount = loopcount + 1
	logger.debug("Loop Count : " + str(loopcount))

	signindivs = browser.find_elements_by_css_selector('#signin-mail')
	if len(signindivs) > 0:
		login()
		WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-game="baccarat"]')))
		tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')
		is_betting = [False] * len(tables)
		prev_count = [0] * len(tables)
		bet_type = [type_normal] * len(tables)
		logger_set()
		continue

	if is_betting.count(True) == 0 and (time.time() - start) > 1500:
		go_to_live()
		WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-game="baccarat"]')))
		tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')
		is_betting = [False] * len(tables)
		prev_count = [0] * len(tables)
		bet_type = [type_normal] * len(tables)
		start = time.time()
		logger_set()
		continue


	tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')

	for i in range(len(tables)):
		try:
			pass
		
			table = tables[i]
			div_tablename = table.find_element_by_css_selector('div[data-role="table-name"]')
			if not div_tablename or not check_table_name(div_tablename.text):
				continue

			table_name = div_tablename.text
			svgs = table.find_elements_by_css_selector('svg[data-role="Big-road"] svg[data-type="coordinates"]')

			if prev_count[i] == len(svgs):
				#配列数が変わらない時はスキップ タイの時も変わらないので不要
				continue
			prev_count[i] = len(svgs)

			dataset = [[None] * dataset_y for k in range(dataset_x)]

			for svg in svgs:
				additem = ()
				child_svg = svg.find_element_by_css_selector('svg[data-type="roadItem"]')
				name = child_svg.get_attribute('name')
				spl = name.split(' ')
				# additem.append(spl[0])
				v = spl[0]
				if v == sp or v == sb or v == st:
					additem = additem + tuple([v])

				if len(spl) > 1 and st in spl[1]:
					if child_svg.text == '':
						# additem.append(st)
						additem = additem + tuple([st])
					else:
						# additem.extend([st] * int(child_svg.text))
						additem = additem + tuple([st] * int(child_svg.text))

				dataset[int(svg.get_attribute('data-x'))][int(svg.get_attribute('data-y'))] = additem

			result_list = from_dataset_to_result(dataset)
			slice_list = result_data_slice(result_list)

			if len(slice_list) == 0:
				#dataが0個
				continue

			now = slice_list[-1]

			if is_skip(result_list,slice_list):
				if is_betting[i]:
					wait_message(table_name)
					is_betting[i] = False
					if len(now) == 3 and str(now[2]) == st:
						#試合数にカウントしない
						total_games = total_games - 1
				continue

			
			last = slice_list[-2]

			print(table_name)
			print(last)
			print(now)

			slice_l = len(now)

			if slice_l == 1:
				check = notice_check(slice_list)
				if check == type_normal or check == type_mirror:
					notice_message(table_name)
					bet_type[i] = check
					is_betting[i] = True

			elif is_betting[i] and slice_l == 2:

				if bet_type[i] == type_normal:
					if check_is_normal(slice_list):
						#ゲーム数の計測
						total_games = total_games + 1
						if last[slice_l] == sp:
							bet_position = sb
						else:
							bet_position = sp
						bet_message(table_name,bet_position)
						continue
					elif now[0] == last[-1]:
						#normal ではなく mirrorの可能性
						bet_type[i] = type_mirror


				if bet_type[i] == type_mirror and check_is_mirror(slice_list):
					#ゲーム数の計測
					total_games = total_games + 1
					bet_position = last[slice_l - 2]
					bet_message(table_name,bet_position)
					continue

				wait_message(table_name)
				is_betting[i] = False
				bet_type[i] = type_normal

			elif is_betting[i] and slice_l >= 3 and slice_l < array_size:

				if bet_type[i] == type_normal and check_is_normal(slice_list):
					if last[slice_l] == sp:
						bet_position = sb
					else:
						bet_position = sp
					bet_message(table_name,bet_position)
					continue

				if bet_type[i] == type_mirror and check_is_mirror(slice_list):
					bet_position = last[slice_l - 2]
					bet_message(table_name,bet_position)
					continue

				is_betting[i] = False
				bet_type[i] = type_normal
				win_games = win_games + 1
				win_message(table_name)

			elif slice_l == array_size:
				if is_betting[i]:
					debug_message = "べットチェック\n" + table_name + "\n"  + bet_type[i] + "\n" 
					debug_message = debug_message + ' '.join(slice_list[-2]) + "\n" + ' '.join(slice_list[-1])
					debug_message = debug_message + "\n\nALL RESULT\n" + ' '.join(result_list)
					logger.debug(debug_message)
				is_betting[i] = False
				bet_type[i] = type_normal


		except Exception as e:
			print(traceback.format_exc())
			pass
		else:
			pass
		finally:
			pass




			




# browser.switch_to.frame(browser.find_element_by_css_selector('.gamelayerGameHolder-holder.lazyFrame.loaded'))
# browser.switch_to.frame(browser.find_element_by_id('game-wrapper'))
# browser.switch_to.frame(browser.find_element_by_id('evolution_wrapper'))

# iframe_array = browser.find_elements_by_css_selector('.loader-frame-container .games-container > iframe')
# prev_count = [0] * len(iframe_array)
# notice_status = [False] * len(iframe_array)
# can_message = [False] * len(iframe_array)
# table_name_list = [""] * len(iframe_array)
# browser.switch_to.frame(iframe_array[0])
# browser.implicitly_wait(1)


# while(True):
# 	clear_global_key()
# 	loopcount = loopcount + 1
# 	logger.debug("Loop Count : " + str(loopcount))

# 	if loopcount % 10000 == 0:
# 		logger_set()

# 	for i in range(len(iframe_array)):

# 		time.sleep(0.25)
# 		browser.switch_to.parent_frame()
# 		browser.switch_to.frame(iframe_array[i])

# 		try:
# 			idle_divs = browser.find_elements_by_css_selector('div[data-role="inactivity-message-clickable"]')
# 			if len(idle_divs) > 0:
# 				browser.execute_script("document.querySelector('div[data-role=\"inactivity-message-clickable\"]').click();")
# 				continue

# 		except Exception as e:
# 			pass
# 		else:
# 			pass
# 		finally:
# 			pass

# 		try:
# 			if table_name_list[i] == "":
# 				table_name_list[i] = browser.find_element_by_css_selector('span[data-role="table-name"]').text
# 				print("supervise on " + table_name_list[i])

# 			result_list = []
# 			slice_list = []
# 			roads = browser.find_elements_by_css_selector('svg[data-role="Bead-road"] svg[data-type="roadItem"]')
# 			if len(roads) == prev_count[i]:
# 				continue

# 			prev_count[i] = len(roads)
# 			for svg in roads:
# 				name = svg.get_attribute('name')
# 				spl = name.split(' ')
# 				result_list.append(spl[0])
# 				pass

# 			if len(result_list) <= array_size or len(result_list) % array_size == 0:
# 				can_message[i] = True
# 				# slice_list is needed for 2 columns
# 				continue

# 			columns_count = math.ceil(len(result_list) / array_size)

# 			for x in range(0,columns_count):
# 				start = x * array_size
# 				end = ( x + 1 ) * array_size
# 				slice_list.append(result_list[start:end])
# 				pass

# 			if slice_list[-2].count(st) > 0 or result_list.count(st)  >= 4:
# 				can_message[i] = False
# 				continue


# 			if len(result_list) % array_size == 1:
# 				check_and_notice(i,table_name_list[i],slice_list)
# 			else:
# 				if not check_is_normal(i,table_name_list[i],slice_list):
# 					if not check_is_mirror(i,table_name_list[i],slice_list):
# 						if can_message[i] and notice_status[i]:
# 							message_text = datetime.datetime.today().strftime("%H:%M ") + table_name_list[i] + " ベットせず待機"
# 							logger.debug(message_text)
# 							message.send_all_message(message_text)
# 							can_message[i] = False
# 						notice_status[i] = False

# 			pass
# 		except Exception as e:
# 			print(traceback.format_exc())
# 		else:
# 			pass
# 		finally:
# 			pass

		

# browser.quit()
# sys.exit()