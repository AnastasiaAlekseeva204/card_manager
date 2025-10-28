import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# Получение токена
auth_data = base64.b64encode(f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}".encode()).decode()
token_response = requests.post('https://ngw.devices.sberbank.ru:9443/api/v2/oauth', 
    headers={'Authorization': f'Basic {auth_data}', 'RqUID': '12345'},
    data={'scope': 'GIGACHAT_API_PERS'}, verify=False)

token = token_response.json()['access_token']

# Распознавание
image_path = input("Путь к изображению: ")
with open(image_path, "rb") as f:
    base64_image = base64.b64encode(f.read()).decode()

response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions', 
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={
        "model": "GigaChat",
        "messages": [{
            "role": "user", 
            "content": [
                {"type": "text", "text": "Распознай визитку: Имя, Должность, Телефон, Email, Компания"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
    }, verify=False)

print(response.json()['choices'][0]['message']['content'])