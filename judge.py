#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
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
empty_skip = 30

bet_balance = 0
win_balance = 0


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

def try_to_default(i):
	global is_betting
	global try_count
	global bet_type
	global bet_target
	try_count[i] = 0
	is_betting[i] = False
	bet_type[i] = type_normal
	bet_target[i] = tuple([])

def try_chance(i,normal_or_mirror):
	global is_betting
	global bet_type
	bet_type[i] = normal_or_mirror
	is_betting[i] = True

def add_try(i,bet_position):
	global try_count
	global bet_target
	global debug_tries
	debug_tries[try_count[i]] = debug_tries[try_count[i]] + 1
	try_count[i] = try_count[i] + 1
	bet_target[i] = bet_target[i] + tuple([bet_position])

def debug_result(message_text,slice_list):
	global total_games
	global win_games
	global tie_games
	global shuffle_games
	
	message_text = message_text + "\n（" + str(total_games) + "戦 " + str(win_games) + "勝 " + str(tie_games) + "タイ " + str(shuffle_games) + "シャッフル）"
	logger.debug(message_text)
	debug_message_text = message_text
	for x in slice_list:
		debug_message_text = debug_message_text + "\n" + ' '.join(x)
		pass
	message.send_debug_message(debug_message_text)

def is_skip(result_list,slice_list):

	if len(slice_list) < 3:
		#2列以下である
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

	return False
	
	# check = True
	# for x in range(1,5):
	# 	if last[x] != st and last[x] == last[x - 1] and last[x] == last[x + 1]:
	# 		check = False
	# 	else:
	# 		pass
	# return check

def notice_check(data):
	now = data[-1]
	last = data[-2]
	if now[0] == st:
		return False
	elif now[0] == last[0]:
		return type_normal
	elif now[0] == last[-1]:
		return type_mirror
	elif now[0] == last[1]:
		return type_normal_mirror

def win_or_false(try_target,bet_target):
	for x in range(len(bet_target)):
		if try_target[x] == bet_target[x]:
			return True

	return False

def check_is_normal(data,try_target,bet_target):
	now = data[-1]
	last = data[-2]
	if now[0] != last[0] or now[1] != last[1]:
		return False

	return not win_or_false(try_target,bet_target)

def check_is_mirror(data,try_target,bet_target):
	now = data[-1]
	last = data[-2]
	if now[0] != last[-1] or now[1] != last[-2]:
		return False

	return not win_or_false(try_target,bet_target)

def check_is_normal_mirror(data,try_target,bet_target):
	now = data[-1]
	last = data[-2]
	if now[0] != last[1] or now[1] != last[0]:
		return False

	return not win_or_false(try_target,bet_target)

def notice_message(i,normal_or_mirror,table_name,slice_list):
	try_chance(i,normal_or_mirror)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nべット準備"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def wait_message(i,table_name,slice_list):
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nベットせず待機"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def shuffle_wait_message(i,table_name,slice_list):
	global shuffle_games
	shuffle_games = shuffle_games + 1
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nベットせず待機"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def tie_wait_message(i,table_name,slice_list):
	global tie_games
	tie_games = tie_games + 1
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nベットせず待機"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def bet_message(i,table_name,target,slice_list):
	global message_bet
	global try_count
	global bet_type
	global type_normal
	global normal_bet
	global reverse_bet

	if try_count[i] < 4:
		if bet_type[i] == type_normal:
			bet_position = reverse_bet[target]
		elif bet_type[i] == type_mirror or bet_type[i] == type_normal_mirror:
			bet_position = normal_bet[target]

	elif try_count[i] >= 4:

		rb = reverse_bet[target]
		if len(slice_list[-1]) == 6:
			tmp_tuple = slice_list[-2] + slice_list[-1]
		else:
			tmp_tuple = slice_list[-3] + slice_list[-2]

		if tmp_tuple.count(st) <= 2 and tmp_tuple.count(rb) == 0:
			bet_position = reverse_bet[target]
		elif bet_type[i] == type_normal:
			bet_position = reverse_bet[target]
		elif try_count[i] % 2 == 0:
			bet_position = reverse_bet[target]
		else:
			bet_position = normal_bet[target]

		# if try_count[i] % 2 == 0:
		# 	bet_position = reverse_bet[target]
		# else:
		# 	bet_position = normal_bet[target]
		
		# elif bet_type[i] == type_normal:
		# 	bet_position = normal_bet[target]
		# elif bet_type[i] == type_mirror or bet_type[i] == type_normal_mirror:
		# 	bet_position = reverse_bet[target]
	
	add_try(i,bet_position)
	message_bet_position = message_bet[bet_position]
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n" + message_bet_position + " " + str(try_count[i])
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def win_message(i,table_name,slice_list):
	global total_games
	global win_games
	win_games = win_games + 1
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n勝ち" 
	message.send_all_message(message_text + "\n（" + str(total_games) + "戦" + str(total_games) + "勝）")
	debug_result(message_text,slice_list)
	file_print(table_name,slice_list)

def game_1_wait_message(i,table_name,slice_list):
	global try_count
	add_try(i,'W')
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nベットせず待機 " + str(try_count[i])
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def lose_message(i,table_name,slice_list):
	global lose_games
	lose_games = lose_games + 1
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n負け" 
	debug_result(message_text,slice_list)
	file_print(table_name,slice_list)

def file_print(table_name,slice_list):
	tmp_tuple = tuple([])
	for l in slice_list:
		tmp_tuple = tmp_tuple + l

	for x in slice_list:
		print(' '.join(x))

	if message.is_production:
		with open('logic_test.txt', 'a') as f:
			print(tmp_tuple, file=f)

def check_prev_count(i,tmp_tuple):
	global prev_count
	if prev_count[i] == tmp_tuple:
		return True
	prev_count[i] = tmp_tuple
	return False

def test_result():
	global win_count
	global lose_count
	global martin_counts
	global win_balance
	global bet_balance

	print("------テスト結果------")
	for i in range(len(martin_counts)):
		print(str(i + 1) + "べット目 : " + str(martin_counts[i]))
	print('win_games : ' + str(win_count))
	print('lose_games : ' + str(lose_count))
	print('bet_balance : $' + str(bet_balance))
	print('win_balance : $' + str(win_balance))

def set_default_value():
	global now_betnumber
	global is_betting
	global bet_count
	now_betnumber = 10000
	is_betting = False
	bet_count = 0

def run(data):
	global number_logs
	global is_betting
	global now_betnumber
	global win_count
	global lose_count
	global bet_count
	global martin_counts
	global target_count
	global max_martin
	global bet_balance
	global win_balance
	number_logs = data
	if len(number_logs) < (empty_skip + target_count + 15):
		return 0

	if not is_betting:
		target = number_logs[target_count + empty_skip]
		if number_logs[(target_count + 1 + empty_skip):(target_count + empty_skip + 16)].count(target) == 1 and number_logs[0:(target_count + empty_skip)].count(target) == 0:
			now_betnumber = target
			is_betting = True
			bet_count = 0
	else:
		#ベット中
		bet_count = bet_count + 1
		if number_logs[0] != now_betnumber:
			if bet_count > max_martin:
				lose_count = lose_count + 1
				print(str(now_betnumber) + " 損切り")
				set_default_value()
				print(str(win_count) + "勝 " + str(lose_count) + "敗")
			else:
				bet_price = round(0.1 + 0.1 * (bet_count - 1),1)
				if bet_count <= 15:
					add = 1
				elif bet_count <= 25:
					add = 2
				else:
					add = 3
				bet_balance = bet_balance + add
				print(str(now_betnumber) + " べット $" + str(bet_price))
		else:
			if bet_count > 1:
				#あたり
				if bet_count <= 16:
					win_add = 1 * 36
				elif bet_count <= 26:
					win_add = 2 * 36
				else:
					win_add = 3 * 36
				win_balance = win_balance + win_add
				win_count = win_count + 1
				martin_counts[bet_count - 1] = martin_counts[bet_count - 1] + 1
				print(str(now_betnumber) + " 当たり（" + str(bet_count) + "べット目）")
				print(str(win_count) + "勝 " + str(lose_count) + "敗")
			else:
				print(str(now_betnumber) + " べット中止")
				
			set_default_value()


