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
version = "1.1.1"

browser = ""

start_time = datetime.now(JST)
start = time.time()
last_bet = time.time()
print_time = time.time()
loopcount = 0
target_table = "スピード オートルーレット"

username = message.username
password = message.password
startURL = "https://www.verajohn.com/ja/livecasino"
liveURL = "https://www.verajohn.com/ja/game/roulette-lobby-paris"
number_logs = tuple([])
prev_tuple = tuple([])
now_betnumber = 10000
is_betting = False
bet_count = 0
win_count = 0
lose_count = 0
max_martin = 30
martin_counts = [0] * max_martin
target_count = 19
empty_skip = 10
continue_win = 0

def login():
	browser.get(startURL)
	time.sleep(1)
	browser.implicitly_wait(10)
	try:
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'signin-mail'))).send_keys(username)
		WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'signin-pass'))).send_keys(password)
		time.sleep(1)
		browser.find_element_by_id('edit-submit-signin--2').click()
	except Exception as e:
		pass
	else:
		pass
	finally:
		pass
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.link.link--alone.js-logout')))
	go_to_live()

def go_to_live():
	global browser
	global target_table
	browser.get(liveURL)
	browser.switch_to.default_content()
	print('go live URL')
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gamelayerGameHolder-holder.lazyFrame.loaded')))
	browser.switch_to.frame(browser.find_element_by_css_selector('.gamelayerGameHolder-holder.lazyFrame.loaded'))
	print('change frame to [.gamelayerGameHolder-holder.lazyFrame.loaded]')
	time.sleep(3)
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'game-wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('game-wrapper'))
	print('change frame to [#game-wrapper]')
	time.sleep(3)
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'evolution_wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('evolution_wrapper'))
	print('change frame to [#evolution_wrapper]')
	time.sleep(5)
	print('jump to table')
	jump = False
	while(not jump):
		WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-role="table-view"]')))
		tables = browser.find_elements_by_css_selector('div[data-role="table-view"]')
		for t in tables:
			spl = t.text.split("\n")
			if target_table in spl:
				actions = ActionChains(browser)
				actions.move_to_element(t)
				actions.click()
				actions.perform()
				jump = True
				break;
	browser.implicitly_wait(1)

def click_continue():
	global browser
	global start
	browser.switch_to.default_content()
	elems = browser.find_elements_by_css_selector('a[data-method="continue"]')
	if len(elems) > 0:
		print('push continue ...')
		for e in elems:
			actions = ActionChains(browser)
			actions.move_to_element(e)
			actions.click()
			actions.perform()

		start = time.time()
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.gamelayerGameHolder-holder.lazyFrame.loaded')))
	browser.switch_to.frame(browser.find_element_by_css_selector('.gamelayerGameHolder-holder.lazyFrame.loaded'))
	print('change frame to [.gamelayerGameHolder-holder.lazyFrame.loaded]')
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'game-wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('game-wrapper'))
	print('change frame to [#game-wrapper]')
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, 'evolution_wrapper')))
	browser.switch_to.frame(browser.find_element_by_id('evolution_wrapper'))
	print('change frame to [#evolution_wrapper]')

def start_browser():
	global browser
	global start_time
	if browser != "":
		browser.quit()
		print("sleep 1 minute ...")
		time.sleep(60)
	message_text = "\nTYPE ROULETTE Ver." + version + "\n起動しました。\n" + datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")
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

def initialize():
	global number_logs
	global prev_tuple
	global now_betnumber
	global is_betting
	global bet_count
	global start
	global last_bet
	global continue_win
	number_logs = tuple([])
	prev_tuple = tuple([])
	now_betnumber = 10000
	is_betting = False
	bet_count = 0
	start = time.time()
	last_bet = time.time()
	continue_win = 0

def set_default_value():
	global now_betnumber
	global is_betting
	global bet_count
	now_betnumber = 10000
	is_betting = False
	bet_count = 0

def print_varsize():
    import types
    print("{}{: >15}{}{: >10}{}".format('|','Variable Name','|','  Size','|'))
    print(" -------------------------- ")
    for k, v in globals().items():
        if hasattr(v, 'size') and not k.startswith('_') and not isinstance(v,types.ModuleType):
            print("{}{: >15}{}{: >10}{}".format('|',k,'|',str(v.size),'|'))
        elif hasattr(v, '__len__') and not k.startswith('_') and not isinstance(v,types.ModuleType):
            print("{}{: >15}{}{: >10}{}".format('|',k,'|',str(len(v)),'|'))

def click_number(number,click_count = 1):
	global browser
	time.sleep(1.7)
	path = browser.find_element_by_css_selector('path[data-bet-spot-id="' + str(number) + '"]')
	actions = ActionChains(browser)
	actions.move_to_element(path)
	actions.click()
	# loop = math.ceil(click_count / 10)
	# for x in range(0,loop):
	# 	actions.perform();
	# 	time.sleep(0.2)
	if click_count > 20:
		actions.perform();
		time.sleep(0.2)

	if click_count > 10:
		actions.perform();
		time.sleep(0.2)

	actions.perform();

def add_number_logs(current_tuple):
	global number_logs
	number_logs = tuple([current_tuple[0]]) + number_logs

def file_print(result_tuple):
	if message.is_production:
		with open('logic_test.txt', 'a') as f:
			print(result_tuple, file=f)

if __name__ == "__main__":
	start_browser()
	initialize()

	while(True):
		loopcount = loopcount + 1
		judge.logger.debug("Loop Count : " + str(loopcount))
		time.sleep(1)

		try:
			tables = browser.find_elements_by_css_selector('div[data-role="table-view"]')
			if len(tables) > 0:
				for t in tables:
					spl = t.text.split("\n")
					if target_table in spl:
						actions = ActionChains(browser)
						actions.move_to_element(t)
						actions.click().perform();
						continue;
		except Exception as e:
			print(traceback.format_exc())
			pass
		else:
			pass
		finally:
			pass

		try:
			if loopcount % 300 == 0:
				click_continue()
				
		except Exception as e:
			pass
		else:
			pass
		finally:
			pass


		try:
			signindivs = browser.find_elements_by_css_selector('#signin-mail')
			if len(signindivs) > 0:
				login()
				initialize()
				continue
		except Exception as e:
			pass
		else:
			pass
		finally:
			pass

		try:
			if is_betting == False and (time.time() - start) > 12000:
				print("Refresh 5s stop ...")
				time.sleep(5)
				start_browser()
				initialize()
				start = time.time()
				continue
		except Exception as e:
			pass
		else:
			pass
		finally:
			pass

		try:
			WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-role="radial-chip"]')))
		except Exception as e:
			print("Refresh 5s stop ...")
			time.sleep(5)
			login()
			initialize()
			continue
		else:
			pass
		finally:
			pass



		try:
			# JSで実行すればいける
			browser.execute_script("document.querySelectorAll('div[data-role=\"radial-chip\"]')[0].click();")

			divs = browser.find_elements_by_css_selector('div[data-role="recent-number"]');
			tmp_tuple = tuple([])

			for d in divs:
				tmp_tuple = tmp_tuple + tuple([d.text])

			if len(prev_tuple) == 0:
				number_logs = tmp_tuple

			elif prev_tuple != tmp_tuple and prev_tuple[-5:] != tmp_tuple[-5:]:
				add_number_logs(tmp_tuple)
				
			else:
				continue

			prev_tuple = tmp_tuple
			print(number_logs[0:100])

			if time.time() - print_time > 1200:
				file_print(number_logs)
				print_time = time.time()

			if len(number_logs) < (empty_skip + target_count + 15):
				continue

			if not is_betting:
				#ベット前
				target = number_logs[target_count + empty_skip]
				if number_logs[(target_count + 1 + empty_skip):(target_count + empty_skip + 16)].count(target) == 1 and number_logs[0:(target_count + empty_skip)].count(target) == 0:
					now_betnumber = target
					is_betting = True
					bet_count = 0
					message.send_debug_message("次に " + str(now_betnumber) + " がでなければべット開始")
					message.beep(2000,500)
			else:
				#ベット中
				bet_count = bet_count + 1
				if number_logs[0] != now_betnumber:
					if bet_count > max_martin:
						lose_count = lose_count + 1
						message.send_debug_message(str(now_betnumber) + " 損切り")
						message.lose_beep(2000,500)
						set_default_value()
						continue_win = 0
						message.send_debug_message(str(win_count) + "勝 " + str(lose_count) + "敗")
						elems = browser.find_elements_by_css_selector('div[data-role="balance-label"]')
						if len(elems) > 0:
							message.send_debug_message(elems[0].text)
						
					else: 
						bet_price = round(0.1 + 0.1 * (bet_count - 1),1)
						message.send_debug_message(str(now_betnumber) + " べット $" + str(bet_price))
						message.beep(2000,500)
						click_number(now_betnumber,bet_count)
						last_bet = time.time()
				else:
					if bet_count > 1:
						#あたり
						win_count = win_count + 1
						message.send_debug_message(str(now_betnumber) + " 当たり（" + str(bet_count) + "べット目）")
						message.win_beep(2000,500)
						message.send_debug_message(str(win_count) + "勝 " + str(lose_count) + "敗")
						elems = browser.find_elements_by_css_selector('div[data-role="balance-label"]')
						if len(elems) > 0:
							message.send_debug_message(elems[0].text)
						continue_win = continue_win + 1
						if continue_win >= 3:
							print('連続3勝なので時間を空けます。')
							time.sleep(1800)
							start_browser()
							initialize()
							start = time.time()
				continue
					else:
						message.send_debug_message(str(now_betnumber) + " べット中止")
					
					set_default_value()




		except Exception as e:
			print(traceback.format_exc())
			pass
		else:
			pass
		finally:
			pass
		
			

	browser.quit()
	sys.exit()