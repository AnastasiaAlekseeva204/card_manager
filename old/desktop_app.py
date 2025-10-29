import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import base64
import requests
from dotenv import load_dotenv
import threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class BusinessCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Распознавание визитных карт")
        self.root.geometry("600x500")
        
        # Кнопка выбора файла
        self.select_button = tk.Button(root, text="Выбрать изображение", 
                                     command=self.select_file, font=("Arial", 12))
        self.select_button.pack(pady=20)
        
        # Метка с именем файла
        self.file_label = tk.Label(root, text="Файл не выбран", fg="gray")
        self.file_label.pack(pady=5)
        
        # Кнопка распознавания
        self.recognize_button = tk.Button(root, text="Распознать", 
                                        command=self.recognize_image, 
                                        font=("Arial", 12), state="disabled")
        self.recognize_button.pack(pady=10)
        
        # Текстовое поле для результата
        self.result_text = scrolledtext.ScrolledText(root, width=70, height=20, 
                                                   font=("Arial", 10))
        self.result_text.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.selected_file = None
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"Выбран: {os.path.basename(file_path)}")
            self.recognize_button.config(state="normal")
    
    def get_token(self):
        credentials = os.getenv('GIGACHAT_CREDENTIALS')
        
        if not credentials:
            return None, "GIGACHAT_CREDENTIALS не найден в .env"
        
        response = requests.post('https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
            headers={
                'Authorization': f'Basic {credentials}',
                'RqUID': '12345',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='scope=GIGACHAT_API_PERS',
            verify=False)
        
        if response.status_code == 200:
            return response.json()['access_token'], None
        else:
            print(f"Отладка: {response.status_code}")
            print(f"Заголовки: {response.headers}")
            print(f"Ответ: {response.text}")
            return None, f"Ошибка {response.status_code}: {response.text}"
    
    def recognize_text_from_image(self, image_path):
        token, error = self.get_token()
        if error:
            return None, error
            
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
            return response.json()['choices'][0]['message']['content'], None
        else:
            return None, f"Ошибка API: {response.status_code}"
    
    def recognize_image(self):
        if not self.selected_file:
            messagebox.showerror("Ошибка", "Выберите файл")
            return
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Распознавание...")
        self.recognize_button.config(state="disabled")
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.process_recognition)
        thread.daemon = True
        thread.start()
    
    def process_recognition(self):
        result, error = self.recognize_text_from_image(self.selected_file)
        
        # Обновление UI в главном потоке
        self.root.after(0, self.update_result, result, error)
    
    def update_result(self, result, error):
        self.result_text.delete(1.0, tk.END)
        
        if error:
            self.result_text.insert(tk.END, f"Ошибка: {error}")
        else:
            self.result_text.insert(tk.END, result)
        
        self.recognize_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessCardApp(root)
    root.mainloop()