import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

def get_token():
    credentials = os.getenv('GIGACHAT_CREDENTIALS')
    
    if not credentials:
        print("Ошибка: GIGACHAT_CREDENTIALS не найден в .env")
        return None
    
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

def recognize_text_from_image(image_path):
    token = get_token()
    if not token:
        return None
        
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode()

    response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={
            "model": "GigaChat",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Распознай текст с этого изображения и выведи его полностью."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }]
        }, verify=False)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Ошибка API: {response.status_code}")
        return None

def main():
    image_path = input("Введите путь к изображению: ")
    
    if not os.path.exists(image_path):
        print(f"Файл {image_path} не найден")
        return
    
    print("Распознаю текст...")
    recognized_text = recognize_text_from_image(image_path)
    
    if recognized_text:
        print("\nРаспознанный текст:")
        print("-" * 50)
        print(recognized_text)
        print("-" * 50)
    else:
        print("Не удалось распознать текст")

if __name__ == "__main__":   
    main()
