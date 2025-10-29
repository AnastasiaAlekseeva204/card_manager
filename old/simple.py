import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

image_path = input("Путь к изображению: ")

with open(image_path, "rb") as f:
    base64_image = base64.b64encode(f.read()).decode()

response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions', 
    headers={'Authorization': f'Bearer {os.getenv("GIGACHAT_API_KEY")}', 'Content-Type': 'application/json'},
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

result = response.json()
print("Ответ API:", result)
if 'choices' in result:
    print(result['choices'][0]['message']['content'])
else:
    print("Ошибка:", result.get('error', 'Неизвестная ошибка'))