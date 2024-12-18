import configparser
import asyncio
import time
import telethon


import requests
api_key = "AIzaSyAcj5Naxr334_-tuAqnK1NbFKl3pghQJoM"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

headers = {
    "Content-Type": "application/json"
}
async def generate_text(text):
  data = {
    "system_instruction": {
      "parts": {
        "text": "Дай оценивающую критику как профессиональный маркетолог посту без указания хештегов и ссылок не более 100 символов"
      }
    },
    "contents": {
      "parts": {
        "text":  text
      }
    }
  }
  response = requests.post(url, headers=headers, json=data)
  try:
    return response.json()['candidates'][0]['content']['parts'][0]['text']
  except Exception:
    return None
async def send_comment(entity, client):
  lsl = await client.get_messages(entity, 1)
  for i in lsl:
    message = i
  try:
    text = await generate_text(message.text)
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