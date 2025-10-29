import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import os
import uuid
import json
from dotenv import find_dotenv, load_dotenv
from langchain_gigachat.chat_models import GigaChat
from langchain_core.runnables import RunnableConfig
from database import save_business_card, SessionLocal, BusinessCard

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
        "content": "Распознай визитную карточку и верни JSON с полями: full_name, status, Company_name, phone_number, adress, email, website, additional_info. Ответ только JSON, никакого дополнительного текста.",
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
            
            entries['website'].delete(0, tk.END)
            entries['website'].insert(0, data.get('website', ''))
            
            entries['additional_info'].delete(0, tk.END)
            entries['additional_info'].insert(0, data.get('additional_info', ''))
            
        except Exception as e:
            for entry in entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, f"Ошибка: {str(e)}")

def save_to_db():
    data = {}
    for field_name, entry in entries.items():
        data[field_name] = entry.get()
    
    try:
        card_id = save_business_card(data)
        messagebox.showinfo("Успех", f"Визитка сохранена в БД с ID: {card_id}")
        load_db_data()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

def load_db_data():
    for item in tree.get_children():
        tree.delete(item)
    
    session = SessionLocal()
    cards = session.query(BusinessCard).all()
    
    for card in cards:
        tree.insert("", "end", values=(
            card.id,
            card.full_name or "",
            card.Company_name or "",
            card.phone_number or "",
            card.email or ""
        ))
    
    session.close()

def on_tree_select(event):
    selection = tree.selection()
    if selection:
        item = tree.item(selection[0])
        card_id = item['values'][0]
        
        session = SessionLocal()
        card = session.query(BusinessCard).filter(BusinessCard.id == card_id).first()
        
        if card:
            entries['full_name'].delete(0, tk.END)
            entries['full_name'].insert(0, card.full_name or "")
            
            entries['status'].delete(0, tk.END)
            entries['status'].insert(0, card.status or "")
            
            entries['Company_name'].delete(0, tk.END)
            entries['Company_name'].insert(0, card.Company_name or "")
            
            entries['phone_number'].delete(0, tk.END)
            entries['phone_number'].insert(0, card.phone_number or "")
            
            entries['adress'].delete(0, tk.END)
            entries['adress'].insert(0, card.adress or "")
            
            entries['email'].delete(0, tk.END)
            entries['email'].insert(0, card.email or "")
            
            entries['website'].delete(0, tk.END)
            entries['website'].insert(0, card.website or "")
            
            entries['additional_info'].delete(0, tk.END)
            entries['additional_info'].insert(0, card.additional_info or "")
        
        session.close()

root = tk.Tk()
root.title("Управление визитными картами")
root.geometry("1000x600")

# Левый фрейм - данные из БД
left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

tk.Label(left_frame, text="База данных визиток", font=("Arial", 14, "bold")).pack(pady=5)

# Таблица
columns = ("ID", "Имя", "Компания", "Телефон", "Email")
tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill="both", expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)

# Правый фрейм - добавление визиток
right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

tk.Label(right_frame, text="Добавление визитки", font=("Arial", 14, "bold")).pack(pady=5)

button = tk.Button(right_frame, text="Выбрать изображение", command=select_and_recognize, font=("Arial", 12))
button.pack(pady=10)

save_button = tk.Button(right_frame, text="Сохранить в БД", command=save_to_db, font=("Arial", 12))
save_button.pack(pady=5)

entries = {}
fields = [
    ("Имя:", "full_name"),
    ("Должность:", "status"), 
    ("Компания:", "Company_name"),
    ("Телефон:", "phone_number"),
    ("Адрес:", "adress"),
    ("Email:", "email"),
    ("Сайт:", "website"),
    ("Доп. инфо:", "additional_info")
]

for label_text, field_name in fields:
    frame = tk.Frame(right_frame)
    frame.pack(pady=5, padx=20, fill="x")
    
    label = tk.Label(frame, text=label_text, width=12, anchor="w")
    label.pack(side="left")
    
    entry = tk.Entry(frame, width=30)
    entry.pack(side="right", fill="x", expand=True)
    
    entries[field_name] = entry

# Загрузка данных при запуске
load_db_data()

root.mainloop()