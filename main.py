import asyncio
import configparser
import time

import telethon
import requests

# Замените значения на свои
API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
MODEL_NAME = "GigaChat"


async def get_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload = 'scope=GIGACHAT_API_PERS'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': '6f0b1291-c7f3-43c6-bb2e-2f3efb3dc98e',
        'Authorization': 'Basic NjFkYjhiZmQtYzVjNS00YjI5LTg1NmItMzY4MTI3MTYzYjlmOjgyMzUzYWU5LTkwZDYtNDdiMi04ZjYyLTg3ODkwNTM5NDAwMw=='
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    n = response.json()
    return response.json()['access_token']


async def generate_comment(text):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {await get_token()}'
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": 'Комментируй полезную критику к посту не больше 100 символов'
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "n": 1,
        "stream": False,
        "max_tokens": 2048,
        "repetition_penalty": 1,
        "update_interval": 0
    }
    try:
        responce =  requests.post(API_URL, headers=headers, json=data, verify=False)
        return responce.json()['choices'][0]['message'][ 'content']
    except Exception as e:
        return None


async def send_comment(entity, client):
    lsl = await client.get_messages(entity, 1)
    for i in lsl:
        message = i
    try:
        text = await generate_comment(message.text)
    except Exception as e:
        return None
    if text and not message.replies:
        try:
            await client.send_message(entity, text, comment_to=message)
        except Exception as e:
            return None

async def get_user_channels():
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_id = int(config['telegram']['api_id'])
    api_hash = config['telegram']['api_hash']
    phone = config['telegram']['phone']
    password = config['telegram']['password']

    client = telethon.TelegramClient('123', api_id, api_hash,
                                     system_version="4.16.30-vxCUSTOM")
    await client.start(phone=phone, password=password)
    while True:
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_channel and not dialog.is_group:
                try:
                    await send_comment(dialog.entity, client)
                    print(dialog.name)
                except Exception:
                    pass
        time.sleep(60)


asyncio.run(get_user_channels())
