import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

def get_token():
    client_id = os.getenv('GIGACHAT_CLIENT_ID')
    client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Ошибка: GIGACHAT_CLIENT_ID или GIGACHAT_CLIENT_SECRET не найдены в .env")
        return None
    
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    response = requests.post('https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
        headers={
            'Authorization': f'Basic {credentials}',
            'RqUID': '12345',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data='scope=GIGACHAT_API_PERS',
        verify=False)
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None

image_path = input("Путь к изображению: ")

with open(image_path, "rb") as f:
    base64_image = base64.b64encode(f.read()).decode()

token = get_token()
if not token:
    exit(1)

response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={
        "model": "GigaChat",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Распознай текст с визитной карты и выдели: Имя, Должность, Телефон, Email, Компания"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
    }, verify=False)

print(response.json()['choices'][0]['message']['content'])