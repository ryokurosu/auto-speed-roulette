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
message_p = 'Player'
message_b = 'Banker'
sp = 'P'
sb = 'B'
st = 'T'
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
is_betting = []
prev_count = []
bet_type = []
is_betting = []

total_games = 0
win_games = 0
tie_games = 0
shuffle_games = 0

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

def set_default_val(length):
	global is_betting
	global prev_count
	global try_count
	global bet_type
	is_betting = [False] * length
	prev_count = [None] * length
	try_count = [0] * length
	bet_type = [type_normal] * length
	logger_set()

def try_to_default(i):
	global is_betting
	global try_count
	global bet_type
	try_count[i] = 0
	is_betting[i] = False
	bet_type[i] = type_normal

def try_chance(i,normal_or_mirror):
	global is_betting
	global bet_type
	bet_type[i] = normal_or_mirror
	is_betting[i] = True

def add_try(i):
	global try_count
	try_count[i] = try_count[i] + 1

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

	if len(slice_list) < 2:
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
	
	check = True
	for x in range(1,5):
		if last[x] != st and last[x] == last[x - 1] and last[x] == last[x + 1]:
			check = False
		else:
			pass
	return check

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

def check_after_4_martin(data,bet_type):
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

def notice_message(i,normal_or_mirror,table_name,slice_list):
	try_chance(i,normal_or_mirror)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nべット準備してください。"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def wait_message(i,table_name,slice_list):
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\nベットせず待機してください。"
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def shuffle_wait_message(i,table_name,slice_list):
	global shuffle_games
	shuffle_games = shuffle_games + 1
	try_to_default(i)
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

def bet_message(i,table_name,bet_position,slice_list):
	global try_count
	try_count[i] = try_count[i] + 1
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n" + bet_position + " " + str(try_count[i])
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def win_message(i,table_name,slice_list):
	global win_games
	win_games = win_games + 1
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n勝ち" 
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def game_1_wait_message(i,table_name,slice_list):
	global try_count
	try_count[i] = try_count[i] + 1
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n1ゲームベットせず待機してください。 " + str(try_count[i])
	message.send_all_message(message_text)
	debug_result(message_text,slice_list)

def lose_message(i,table_name,slice_list):
	try_to_default(i)
	message_text = datetime.now(JST).strftime("%H:%M ") + table_name + "\n負け" 
	debug_result(message_text,slice_list)

def check_prev_count(i,tmp_tuple):
	global prev_count
	if prev_count[i] == tmp_tuple:
		return True
	prev_count[i] = tmp_tuple
	return False

def exec(i,table_name,result_list,slice_list):
	global is_betting
	global try_count
	global bet_type
	global total_games

	if len(slice_list) < 2:
		#dataが0個
		if try_count[i] > 0:
			shuffle_wait_message(i,table_name,slice_list)
		return 0;

	now = slice_list[-1]

	if try_count[i] == 1:
		#ゲーム数の計測
		total_games = total_games + 1

	if not is_betting[i] and is_skip(result_list,slice_list):
		return 0;

			
	last = slice_list[-2]

	print(table_name)
	print(last)
	print(now)

	slice_l = len(now)

	if not is_betting[i] and try_count[i] == 0 and slice_l == 1:
		check = notice_check(slice_list)
		if check == type_normal or check == type_mirror:
			notice_message(i,check,table_name,slice_list)

	elif is_betting[i] and try_count[i] == 0:

		if bet_type[i] == type_normal:
			if check_is_normal(slice_list):
				bet_position = reverse_bet[last[slice_l]]
				bet_message(i,table_name,bet_position,slice_list)
				return 0;
		elif now[0] == last[-1]:
			#normal ではなく mirrorの可能性
			bet_type[i] = type_mirror


		if bet_type[i] == type_mirror and check_is_mirror(slice_list):
			bet_position = normal_bet[last[slice_l - 2]]
			bet_message(i,table_name,bet_position,slice_list)
			return 0;

		wait_message(i,table_name,slice_list)
		return 0;

	elif is_betting[i] and try_count[i] <= 3:

		if now[slice_l - 1] == st:
			if try_count[i] == 1 or try_count[i] == 2:
				tie_wait_message(i,table_name,slice_list)
			# continue

		if bet_type[i] == type_normal and check_is_normal(slice_list):
			bet_position = reverse_bet[last[slice_l]]
			bet_message(i,table_name,bet_position,slice_list)
			return 0;

		if bet_type[i] == type_mirror and check_is_mirror(slice_list):
			bet_position = normal_bet[last[slice_l - 2]]
			bet_message(i,table_name,bet_position,slice_list)
			return 0;

		win_message(i,table_name,slice_list)

	elif is_betting[i] and try_count[i] == 4:

		if check_before_row_4_martin(slice_list,bet_type[i]):
			if bet_type[i] == type_normal:
				bet_position = normal_bet[now[0]]
			else:
				bet_position = reverse_bet[now[0]]
			bet_message(i,table_name,bet_position,slice_list)
			return 0;
		win_message(i,table_name,slice_list)


	elif is_betting[i] and try_count[i] >= 5 and try_count[i] <= 8:

		if check_after_4_martin(slice_list,bet_type[i]):

			if bet_type[i] == type_normal:
				bet_position = normal_bet[last[slice_l]]
			else:
				bet_position = reverse_bet[last[slice_l]]
			bet_message(i,table_name,bet_position,slice_list)
			return 0;
		elif last[slice_l] == st:
			#前列がタイ
			game_1_wait_message(i,table_name,slice_list)
			return 0;
				
		win_message(i,table_name,slice_list)


	elif try_count[i] == 9:
		if not check_after_4_martin(slice_list,bet_type[i]):
			win_message(i,table_name,slice_list)
		elif is_betting[i]:
			lose_message(i,table_name,slice_list)
				
		try_to_default(i)



