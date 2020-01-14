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
import os
import sys
import message
import traceback
import fractions
import subprocess
from logging import getLogger, StreamHandler, DEBUG, FileHandler, Formatter


nowdate = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
logger = getLogger(__name__)
handler = StreamHandler()
handler = FileHandler(filename="./logs/" + nowdate + ".log", encoding="utf-8")
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("-----------------------\n%(asctime)s %(levelname)8s %(message)s"))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

version = "2.0.0"

filter_time = 65;
filter_time_after = 75;
filter_count_under = 4;
filter_count_score = 3;
filter_odds = 1.10;
filter_count = 5;

browser = ""
start_time = datetime.datetime.now()
notified = []
loopcount = 0

startURL = "https://mobile.bet365.com/?nr=1#/IP/"


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

def timer_check(a_team,b_team,a_team_count,b_team_count,play_timer):
	time_array = play_timer.split(':')
	if time_array[0] == "ET" or int(time_array[0]) < filter_time or int(time_array[0]) > filter_time_after:
		# now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
		# message_text = "[Check Rule]\n"\
		# "[種目]サッカー\n"\
		# "[試合]" + a_team + " VS " + b_team +  "\n"\
		# "[経過時間]" + play_timer +  "\n"\
		# "[ベット対象]Alternative Match Goals\n"\
		# "[時間]" + now + "\n[Jodge]Timer Check"
		# logger.debug(message_text)
		return False
	return True

def count_filter(a_team_count,b_team_count):
	if int(a_team_count) >= filter_count_score or int(b_team_count) >= filter_count_score:
		return False
	return True

def easy_check(play_timer,a_team,b_team,a_team_count, b_team_count,under,odds):
	if odds > filter_odds:
		now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
		message_text = "[Check Rule]\n"\
		"[種目]サッカー\n"\
		"[試合]" + a_team + " VS " + b_team +  "\n"\
		"[経過時間]" + play_timer +  "\n"\
		"[時間]" + now + "\n[Jodge]Easy Check\n"\
		"[URL]" + browser.current_url
		logger.debug(message_text)
		return False
	return True


def check_rules(play_timer, a_team, b_team, a_team_count, b_team_count, under, odds):
	now = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
	message_text = "[Check Rule]\n"\
	"[種目]サッカー\n"\
	"[試合]" + a_team + " VS " + b_team +  "\n"\
	"[経過時間]" + play_timer +  "\n"\
	"[ベット対象]Alternative Match Goals\n"\
	"[カウント]" + str(under) + " under\n"\
	"[オッズ]" + str(odds) + "以下\n"\
	"[スコア]" + str(a_team_count) + " - " + str(b_team_count) + "\n"\
	"[時間]" + now + "\n[Jodge]HIT\n"\
	"[URL]" + browser.current_url + "\n"

	check = True

	if float(a_team_count) + float(b_team_count) + filter_count_under > float(under):
		message_text = message_text + "Status : a_team_count + b_team_count + "+str(filter_count_under) +" > under\n"
		check = False

	if int(a_team_count) + int(b_team_count) >= filter_count:
		message_text = message_text + "Status : a_team_count + b_team_count >= " + str(filter_count) + "\n"
		check = False

	logger.debug(message_text)
	return check

def check_notified(a_team, b_team, notified):
	mylist = [a_team,b_team]
	for n in notified:
		if mylist == n:
			return True
		else:
			pass
	return False

def start_browser():
	global browser
	global start_time
	if browser != "":
		browser.quit()
	message_text = "起動しました SLB Ver." + version + "\n" + datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
	start_time = datetime.datetime.now()
	logger.debug(message_text)
	message.send_debug_message(message_text)
	uas = ["Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
	"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36",
	"Mozilla/5.0 (Linux; U; Android 4.3; en-us; SM-N900T Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
	"Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36"]
	# random.shuffle(uas)
	base = os.path.dirname(os.path.abspath(__file__))
	options = webdriver.ChromeOptions()
	mobile_emulation = {
	    "deviceMetrics": { "width": 1024, "height": 1366, "pixelRatio": 3.0 },
	    "userAgent": uas[0] }
	options.add_argument('--no-sandbox')
	options.add_argument('--lang=ja-JP')
	options.add_argument("--incognito")
	options.add_experimental_option("mobileEmulation", mobile_emulation)
	if os.name == 'nt':
		browser = webdriver.Chrome(os.path.normpath(os.path.join(base, "./chromedriver.exe")),options=options)
	else:
		browser = webdriver.Chrome(os.path.normpath(os.path.join(base, "./chromedriver")),options=options)
	browser.get("https://www.google.com/?hl=ja")
	browser.implicitly_wait(2)
	browser.get(startURL)
	logger_set()
	soccer_click()


def soccer_click():
	check = False
	for b in browser.find_elements_by_css_selector('.hm-TabletNavButtons_Link'):
		if "In-Play" in b.text:
			try:
				b.click()
			except Exception as e:
				print(traceback.format_exc())
				pass
			else:
				pass
			finally:
				pass
			

	stop_count = 0
	while(not check):
		logger.debug('Searching Soccer... ' + str(stop_count))
		buttons = browser.find_elements_by_css_selector('.ipo-ClassificationMenuBase .ipo-Classification')
		stop_count = stop_count + 1
		if stop_count > 50:
			check = True
			break

		for b in buttons:
			try:
				classname = b.text
				if 'Soccer' in classname:
					time.sleep(3)
					b.click()
					logger.debug('go Soccer Page')
					check = True
					break
			except Exception as e:
				print(traceback.format_exc())
				pass
			else:
				pass
			finally:
				pass

def clear_global_key():
	global rows
	rows = "cleared"
	global row
	row = "cleared"
	global buttons
	buttons = "cleared"
	global b
	b = "cleared"

start_browser()

row_index = 0
loop_stop_count = 0
skip_count = 0

# input()

while(True):
	try:
		loopcount = loopcount + 1
		logger.debug("Loop Count : " + str(loopcount))

		if loopcount % 300000 == 0:
			message_text = "正常に稼働中...\n" + datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
			logger.debug(message_text)
			message.send_debug_message(message_text)
			logger_set()
					
		elif loopcount % 30000 == 0:
			browser.get(startURL)
			logger_set()
			soccer_click()
		elif loop_stop_count  % 15 == 14:
			print(loop_stop_count)
			browser.get(startURL)
			print('sleep 5 seconds')
			time.sleep(5)
			soccer_click()

		browser.implicitly_wait(1)

		rows = browser.find_elements_by_css_selector('.ipo-FixtureList .ipo-Fixture.ipo-Fixture_TimedFixture')
		if len(rows) == 0:
			loop_stop_count = loop_stop_count + 1
			continue
		elif len(rows) <= row_index:
			row_index = 0
			pass

		loop_stop_count = 0
		try:
			row = rows[row_index]
			gamedata = row.text.split('\n')
		except Exception as e:
			continue
		else:
			pass
		finally:
			pass

		try:
			if len(gamedata) < 5:
				skip_count = skip_count + 1
				continue
			a_team = gamedata[0]
			a_team_count = gamedata[1]
			b_team = gamedata[2]
			b_team_count = gamedata[3]
			play_timer = gamedata[4]
			if not timer_check(a_team,b_team,a_team_count,b_team_count,play_timer) or not count_filter(a_team_count,b_team_count) or check_notified(a_team,b_team,notified):
				continue

			try:
				action = ActionChains(browser)
				action.move_to_element(row).perform()
				row.click()
				title = browser.find_element_by_css_selector('.ipe-EventViewTitle_Text.ipe-EventViewTitle_TextArrow').text

				# row が一致しないときのための処理
				if a_team in title and b_team in title:
					print(a_team + " v " + b_team)
					for market in browser.find_elements_by_css_selector('.ipe-Market'):
						if "Match Goals" in market.text:
							market_data = market.text.split('\n')
							if len(market_data) <= (market_data.index('Under') + 1):
								break
							del market_data[0]
							print(market_data)
							under_array = market_data[1:market_data.index('Over')]
							odds_array = market_data[market_data.index('Under') + 1:]
							for i in range(len(under_array)):
								under = under_array[i]
								odds = odds_array[i]
								if odds is not '':
									try:
										odds = 1 + float(fractions.Fraction(odds))
										odds = round(odds,2)
									except Exception as e:
										continue
									else:
										pass
									finally:
										pass
								else:
									print('odds is empty')
									continue

								if easy_check(play_timer,a_team,b_team,a_team_count, b_team_count,under,odds) and check_rules(play_timer, a_team, b_team, a_team_count, b_team_count, under, odds):
									message.send_debug_message("HIT!")
									googleurl = "https://www.google.com/search?q=" + urllib.parse.quote(a_team + " VS " + b_team)
									message_text = "／\nSLB配信 ベット通知\n＼\n\n"\
													"【種目】サッカー\n" + a_team + " VS " + b_team +  "\n"\
								                    "（" + str(a_team_count) + " - " + str(b_team_count) + "） " + play_timer + "\n"\
								                    "【ベット対象】\nMatch Goals\n" + str(under) + "\nUnder\n\n"\
								                    "【現在のオッズ】" + str(odds) + "\n\n"\
								                    "下のURLから直接ベットしてください。↓↓\n"\
								                    "【ベットURL】\n" + browser.current_url + "\n"\
								                    "\n※時間経過により、オッズが微妙に変動している可能性があります。\n\nPowered by SLB.\n" + datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S") + "\n\n試合結果URL：" + googleurl
									message.send_all_message(message_text)
									message.send_debug_message(message_text)

									rowValue = [datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"), a_team, b_team, a_team_count, b_team_count, play_timer, odds, under]
									message.append_sheet_value(rowValue)

									logger.debug('send Line Message')
									logger.debug(message_text)

									teamset = [a_team,b_team]
									notified.append(teamset)
									print("Notified Team List")
									print(notified)
									print("=========================")
									break
							break

				browser.back()

			except Exception as e:
				print(traceback.format_exc())
				# browser.get(startURL)
			else:
				pass
			finally:
				pass

		except Exception as e:
			skip_count = skip_count + 1
			print(traceback.format_exc())
			continue
		else:
			pass
		finally:
			row_index = row_index + 1
			clear_global_key()
			# elapsed_time = time.time() - start_time
			# print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
			pass
		continue
	except Exception as e:
		print(traceback.format_exc())
		continue
	else:
		pass
	finally:
		pass
	# start_time = time.time()

browser.quit()
sys.exit()