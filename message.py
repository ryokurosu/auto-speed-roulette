#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
from os.path import join, dirname
from dotenv import load_dotenv
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import datetime


load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

line_bot_api = LineBotApi(os.environ.get("ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_ID"))

debug_line_bot_api = LineBotApi(os.environ.get("DEBUG_ACCESS_TOKEN"))





app_env = ""
if os.environ.get("APP_ENV"):
	app_env = os.environ.get("APP_ENV")
else:
	app_env = "本番用"



def send_group_message(group_id,message_text):
    try:
        line_bot_api.push_message(
        group_id,
        TextSendMessage(text=message_text))
    except Exception as e:
        pass
    else:
        pass
    finally:
        pass
    

def send_all_message(message_text):
    try:
        line_bot_api.broadcast(TextSendMessage(text=message_text))
    except Exception as e:
        pass
    else:
        pass
    finally:
        pass
    

def send_debug_message(message_text):
    try:
        message_text = app_env + "\n" + message_text
        debug_line_bot_api.broadcast(TextSendMessage(text=message_text))
    except Exception as e:
        pass
    else:
        pass
    finally:
        pass

def append_sheet_value(rowValue):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

    #OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)
    spreadsheetId = '1DnbMdfgYHwR69xeYTvd-LP0YeuHeFC9ZHPDJ7hdTrxQ'
    sheet = gc.open_by_key(spreadsheetId).worksheet('Result') 
    sheet.append_row(rowValue)

if __name__ == "__main__":
    # send_debug_message('hello')
    append_sheet_value()