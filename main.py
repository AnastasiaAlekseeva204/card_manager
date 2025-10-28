import os
import sys
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def recognize_business_card(image_path):
    api_key = os.getenv('GIGACHAT_API_KEY')
    if not api_key:
        print("Ошибка: GIGACHAT_API_KEY не найден в .env файле")
        return None
    
    base64_image = encode_image(image_path)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Распознай информацию с визитной карты и выдели: Имя, Должность, Телефон, Адрес, Email, Компания, Дополнительная информация"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }
    
    response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions', 
                           headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Ошибка API: {response.status_code}")
        return None

def save_to_file(content, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Результат сохранен в {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Использование: python main.py <путь_к_изображению>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Файл {image_path} не найден")
        sys.exit(1)
    
    print("Распознавание визитной карты...")
    result = recognize_business_card(image_path)
    
    if result:
        output_file = "business_card_info.txt"
        save_to_file(result, output_file)
    else:
        print("Не удалось распознать визитную карту")

if __name__ == "__main__":
    main()