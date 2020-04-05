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
import traceback
import fractions
import subprocess
from dotenv import load_dotenv
from logging import getLogger, StreamHandler, DEBUG, FileHandler, Formatter
from selenium.common.exceptions import NoSuchElementException 


JST = timezone(timedelta(hours=+9), 'JST')
nowdate = datetime.now(JST).strftime("%Y%m%d_%H%M%S")
logger = getLogger(__name__)
handler = StreamHandler()
handler = FileHandler(filename="./logs/" + nowdate + ".log", encoding="utf-8")
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("-----------------------\n%(asctime)s %(message)s\n"))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

version = "1.0.2"
array_size = 6
dataset_x = 40
dataset_y = 6

browser = ""
is_betting = []
prev_count = []
bet_type = []

start_time = datetime.now(JST)
start = time.time()
loopcount = 0

username = message.username
password = message.password
startURL = "https://www.verajohn.com/ja/livecasino"
liveURL = "https://www.verajohn.com/ja/game/baccarat-lobby-paris"
sp = 'P'
sb = 'B'
st = 'T'
message_p = 'Player'
message_b = 'Banker'
normal_bet = {}
normal_bet[sp] = message_p
normal_bet[sb] = message_b
normal_bet[st] = st
reverse_bet = {}
reverse_bet[sp] = message_b
reverse_bet[sb] = message_p
reverse_bet[st] = st
type_normal = 'normal'
type_mirror = 'mirror'
# use_tables = ["バカラ A","バカラ B","バカラ C","バカラスクイーズ","バカラコントロールスクイーズ"]
use_tables = ["スピードバカラ A","スピードバカラ B","スピードバカラ C","バカラ A","バカラ B","バカラ C","バカラスクイーズ","バカラコントロールスクイーズ"]

total_games = 0
win_games = 0
tie_games = 0
shuffle_games = 0

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
	time.sleep(15)
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gamelayerGameHolder-holder.lazyFrame.loaded')))
	browser.switch_to.frame(browser.find_element_by_css_selector('.gamelayerGameHolder-holder.lazyFrame.loaded'))
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'game-wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('game-wrapper'))
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'evolution_wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('evolution_wrapper'))
	browser.implicitly_wait(1)

#############################################

def logger_set():
	global logger
	for h in logger.handlers:
		logger.removeHandler(h)
	nowdate = datetime.now(JST).strftime("%Y%m%d_%H%M%S")
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
		if now[x] != st and now[x] != last[x]:
			return False

	return True

def check_is_mirror(data):
	now = data[-1]
	last = data[-2]
	if now[0] != last[-1] or now[1] != last[-2]:
		return False

	for x in range(2,len(now)):
		if now[x] != st and now[x] == last[x - 2]:
			return False

	return True

def check_before_row_4_martin(data,bet_type):
	if bet_type == type_normal:
		return check_is_normal(data)
	elif bet_type == type_mirror:
		return check_is_mirror(data)

	return False

def check_after_4_martin(data):
	now = data[-1]
	last = data[-2]

	if bet_type == type_normal:
		for x in range(0,len(now)):
			if now[x] != st and now[x] == last[x]:
				return False

	elif bet_type == type_mirror:
		for x in range(0,len(now)):
			if now[x] != st and now[x] != last[x]:
				return False

	return True

def notice_message(table_name,slice_list):
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nべット準備してください。"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def wait_message(i,table_name,slice_list):
	try_count[i] = 0
	is_betting[i] = False
	bet_type[i] = type_normal
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nベットせず待機してください。"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def shuffle_wait_message(i,table_name,slice_list):
	global shuffle_games
	shuffle_games = shuffle_games + 1
	try_count[i] = 0
	is_betting[i] = False
	bet_type[i] = type_normal
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nシャッフルの為ベットせず待機してください。"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def tie_wait_message(i,table_name,slice_list):
	global tie_games
	tie_games = tie_games + 1
	# try_count[i] = try_count[i] + 1
	# try_count[i] = 0
	# is_betting[i] = False
	# bet_type[i] = type_normal
	# message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nタイの為ベットせず待機次のテーブルや指示からBETの続きを再開してください。"
	# message.send_all_message(message_text)
	# debug_result(message_text,slice_list)

def bet_message(table_name,bet_position,slice_list,try_count):
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n" + bet_position + " " + str(try_count)
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def win_message(table_name,slice_list):
	global win_games
	win_games = win_games + 1
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n勝ち" 
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def game_1_wait_message(table_name,slice_list,try_count):
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n1ゲームベットせず待機してください。 " + str(try_count)
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def lose_message(table_name,slice_list):
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n負け" 
	debug_result(message_text,slice_list)

def debug_result(message_text,slice_list):
	message_text = message_text + "\n（" + str(total_games) + "戦 " + str(win_games) + "勝 " + str(tie_games) + "タイ " + str(shuffle_games) + "シャッフル）"
	logger.debug(message_text)
	debug_message_text = message_text
	for x in slice_list:
		debug_message_text = debug_message_text + "\n" + ' '.join(x)
		pass
	message.send_debug_message(debug_message_text)

################################################################

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

	if last.count(st) > 0 or now.count(st) > 0:
		#前列・今列がタイ
		return True
	
	if result_list.count(st) - now.count(st) >= 4:
		#タイが4つ以上
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
try_count = [0] * len(tables)
prev_count = [None] * len(tables)
bet_type = [type_normal] * len(tables)

while(True):
	clear_global_key()
	loopcount = loopcount + 1
	logger.debug("Loop Count : " + str(loopcount))
	time.sleep(0.5)

	signindivs = browser.find_elements_by_css_selector('#signin-mail')
	if len(signindivs) > 0:
		login()
		WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-game="baccarat"]')))
		tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')
		is_betting = [False] * len(tables)
		prev_count = [None] * len(tables)
		try_count = [0] * len(tables)
		bet_type = [type_normal] * len(tables)
		logger_set()
		continue

	if is_betting.count(True) == 0 and (time.time() - start) > 1200:
		go_to_live()
		WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-game="baccarat"]')))
		tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')
		is_betting = [False] * len(tables)
		prev_count = [None] * len(tables)
		try_count = [0] * len(tables)
		bet_type = [type_normal] * len(tables)
		start = time.time()
		logger_set()
		continue


	tables = browser.find_elements_by_css_selector('div[data-game="baccarat"]')

	for i in range(len(tables)):
		try:
			table = tables[i]
			div_tablename = table.find_element_by_css_selector('div[data-role="table-name"]')
			if not div_tablename or not check_table_name(div_tablename.text):
				continue

			table_name = div_tablename.text
			road_item_colors = table.find_elements_by_css_selector('g[data-type="roadItemColor"]')
			tmp = table.text.split("\n")
			tmp_tuple = tuple([len(road_item_colors)]) + tuple(tmp[1:-3])

			svgs = table.find_elements_by_css_selector('svg[data-role="Big-road"] svg[data-type="coordinates"]')

			if prev_count[i] == tmp_tuple:
				#最後同じ場合・変わらない時はスキップ
				continue
			prev_count[i] = tmp_tuple

			dataset = [[None] * dataset_y for k in range(dataset_x)]

			

			for svg in svgs:
				additem = ()
				child_svg = svg.find_element_by_css_selector('svg[data-type="roadItem"]')
				name = child_svg.get_attribute('name')
				spl = name.split(' ')
				# additem.append(spl[0])
				v = spl[0][0]
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


			################################################################
			if len(slice_list) == 0:
				#dataが0個
				if try_count[i] > 0:
					shuffle_wait_message(i,table_name,slice_list)
				continue

			now = slice_list[-1]

			if try_count[i] == 1:
				#ゲーム数の計測
				total_games = total_games + 1

			if not is_betting[i] and is_skip(result_list,slice_list):
				continue

			
			last = slice_list[-2]

			print(table_name)
			print(last)
			print(now)

			slice_l = len(now)

			if not is_betting[i] and try_count[i] == 0 and slice_l == 1:
				check = notice_check(slice_list)
				if check == type_normal or check == type_mirror:
					notice_message(table_name,slice_list)
					bet_type[i] = check
					is_betting[i] = True

			elif is_betting[i] and try_count[i] == 0:

				if bet_type[i] == type_normal:
					if check_is_normal(slice_list):
						bet_position = reverse_bet[last[slice_l]]
						try_count[i] = try_count[i] + 1
						bet_message(table_name,bet_position,slice_list,try_count[i])
						continue
					elif now[0] == last[-1]:
						#normal ではなく mirrorの可能性
						bet_type[i] = type_mirror


				if bet_type[i] == type_mirror and check_is_mirror(slice_list):
					bet_position = normal_bet[last[slice_l - 2]]
					try_count[i] = try_count[i] + 1
					bet_message(table_name,bet_position,slice_list,try_count[i])
					continue

				wait_message(i,table_name,slice_list)
				continue

			elif is_betting[i] and try_count[i] <= 3:

				if now[slice_l - 1] == st:
					if try_count[i] == 1 or try_count[i] == 2:
						tie_wait_message(i,table_name,slice_list)
					# continue

				if bet_type[i] == type_normal and check_is_normal(slice_list):
					bet_position = reverse_bet[last[slice_l]]
					try_count[i] = try_count[i] + 1
					bet_message(table_name,bet_position,slice_list,try_count[i])
					continue

				if bet_type[i] == type_mirror and check_is_mirror(slice_list):
					bet_position = normal_bet[last[slice_l - 2]]
					try_count[i] = try_count[i] + 1
					bet_message(table_name,bet_position,slice_list,try_count[i])
					continue

				is_betting[i] = False
				bet_type[i] = type_normal
				try_count[i] =  0
				win_message(table_name,slice_list)

			elif is_betting[i] and try_count[i] == 4:

				if check_before_row_4_martin(slice_list,bet_type[i]):
					if bet_type[i] == type_normal:
						bet_position = normal_bet[now[0]]
					else:
						bet_position = reverse_bet[now[0]]
					try_count[i] = try_count[i] + 1
					bet_message(table_name,bet_position,slice_list,try_count[i])
					continue

				is_betting[i] = False
				bet_type[i] = type_normal
				try_count[i] =  0
				win_message(table_name,slice_list)


			elif is_betting[i] and try_count[i] >= 5 and try_count[i] <= 8:

				if check_after_4_martin(slice_list):
					if bet_type[i] == type_normal:
						bet_position = normal_bet[last[slice_l]]
					else:
						bet_position = reverse_bet[last[slice_l]]
					try_count[i] = try_count[i] + 1
					bet_message(table_name,bet_position,slice_list,try_count[i])
					continue
				elif last[slice_l] == st:
					#前列がタイ
					try_count[i] = try_count[i] + 1
					game_1_wait_message(table_name,slice_list,try_count[i])
					continue
					
				is_betting[i] = False
				bet_type[i] = type_normal
				try_count[i] =  0
				win_message(table_name,slice_list)


			elif try_count[i] == 9:
				if is_betting[i]:
					lose_message(table_name,slice_list)
				is_betting[i] = False
				bet_type[i] = type_normal
				try_count[i] = 0

		except Exception as e:
			print(traceback.format_exc())
			pass
		else:
			pass
		finally:
			pass
		######################################################

browser.quit()
sys.exit()