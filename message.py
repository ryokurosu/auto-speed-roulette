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
import urllib.request
import urllib.parse
import json
import telegram



load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

line_bot_api = LineBotApi(os.environ.get("ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_ID"))
room_id = os.environ.get("ROOM_ID")
token = os.environ.get("TOKEN")

debug_line_bot_api = LineBotApi(os.environ.get("DEBUG_ACCESS_TOKEN"))

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

bot = telegram.Bot(token=os.environ.get("TELEGRAM_TOKEN"))
chat_id=os.environ.get("TELEGRAM_CHAT_ID")
debug_chat_id=os.environ.get("TELEGRAM_DEBUG_CHAT_ID")

app_env = ""
if os.environ.get("APP_ENV"):
    app_env = os.environ.get("APP_ENV")
else:
    app_env = "本番用"

def beep(freq, dur=100):
    if os.name == 'nt':
        # Windowsの場合は、winsoundというPython標準ライブラリを使います.
        import winsound
        winsound.Beep(freq, dur)
    else:
        # Macの場合には、Macに標準インストールされたplayコマンドを使います.
        os.system('afplay /System/Library/Sounds/Submarine.aiff')

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
    beep(2000,500)
    print('*******************')
    print(message_text)
    print('*******************')
    try:
        bot.send_message(chat_id=chat_id, text=message_text)
    except Exception as e:
        pass
    else:
        pass
    finally:
        pass
    
    return True
    
    try:
        # line_bot_api.broadcast(TextSendMessage(text=message_text))
        payload = {'message': message_text}
        json_data = json.dumps(payload).encode("utf-8")
        method = "POST"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }
        request = urllib.request.Request('https://synplace.com/api/mobileapp/rooms/' + room_id + '/post/newmessage',data=json_data,method=method,headers=headers)
        response = urllib.request.urlopen(request)
        print(response.getcode())
        html = response.read()
        print(html.decode('utf-8'))
    except Exception as e:
        print(e)
        pass
    else:
        pass
    finally:
        pass
    

def send_debug_message(message_text):
    try:
        bot.send_message(chat_id=debug_chat_id, text=message_text)
    except Exception as e:
        pass
    else:
        pass
    finally:
        pass
    
    return True

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
    send_all_message('test')