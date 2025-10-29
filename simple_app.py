import tkinter as tk
from tkinter import filedialog, scrolledtext
import os
import uuid
import json
from dotenv import find_dotenv, load_dotenv
from langchain_gigachat.chat_models import GigaChat
from langchain_core.runnables import RunnableConfig

load_dotenv(find_dotenv())

def recognize_text_from_image(image_path):
    model = GigaChat(
        model="GigaChat-2-Max",
        verify_ssl_certs=False,
    )
    
    with open(image_path, "rb") as image_file:
        file_uploaded_id = model.upload_file(image_file).id_
    
    config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})
    
    message = {
        "role": "user",
        "content": "Распознай визитную карточку и верни JSON с полями: full_name, status, Company_name, phone_number, adress, email. Ответ только JSON, никакого дополнительного текста.",
        "attachments": [file_uploaded_id]
    }
    
    response = model.invoke(
        [message],
        config=config
    )
    
    print(response.content)
    return response.content

def select_and_recognize():
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
    if file_path:
        for entry in entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "Распознавание...")
        root.update()
        
        try:
            result = recognize_text_from_image(file_path)
            data = json.loads(result)
            
            entries['full_name'].delete(0, tk.END)
            entries['full_name'].insert(0, data.get('full_name', ''))
            
            entries['status'].delete(0, tk.END)
            entries['status'].insert(0, data.get('status', ''))
            
            entries['Company_name'].delete(0, tk.END)
            entries['Company_name'].insert(0, data.get('Company_name', ''))
            
            entries['phone_number'].delete(0, tk.END)
            entries['phone_number'].insert(0, data.get('phone_number', ''))
            
            entries['adress'].delete(0, tk.END)
            entries['adress'].insert(0, data.get('adress', ''))
            
            entries['email'].delete(0, tk.END)
            entries['email'].insert(0, data.get('email', ''))
            
        except Exception as e:
            for entry in entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, f"Ошибка: {str(e)}")

root = tk.Tk()
root.title("Распознавание визитных карт")
root.geometry("400x300")

button = tk.Button(root, text="Выбрать изображение", command=select_and_recognize, font=("Arial", 12))
button.pack(pady=10)

entries = {}
fields = [
    ("Имя:", "full_name"),
    ("Должность:", "status"), 
    ("Компания:", "Company_name"),
    ("Телефон:", "phone_number"),
    ("Адрес:", "adress"),
    ("Email:", "email")
]

for label_text, field_name in fields:
    frame = tk.Frame(root)
    frame.pack(pady=5, padx=20, fill="x")
    
    label = tk.Label(frame, text=label_text, width=10, anchor="w")
    label.pack(side="left")
    
    entry = tk.Entry(frame, width=30)
    entry.pack(side="right", fill="x", expand=True)
    
    entries[field_name] = entry

root.mainloop()