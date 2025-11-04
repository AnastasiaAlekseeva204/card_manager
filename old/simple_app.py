import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import os
import uuid
import json
from dotenv import find_dotenv, load_dotenv
from langchain_gigachat.chat_models import GigaChat
from langchain_core.runnables import RunnableConfig
from database import save_business_card, SessionLocal, BusinessCard, Company
from sqlalchemy import text

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

def add_new():
    for entry in entries.values():
        entry.delete(0, tk.END)
    sql_text.delete(1.0, tk.END)
    sql_text.insert(tk.END, "# Новая запись")
    sqlalchemy_text.delete(1.0, tk.END)
    sqlalchemy_text.insert(tk.END, "# Очистка формы")

def save_to_db():
    data = {}
    for field_name, entry in entries.items():
        data[field_name] = entry.get()
    
    try:
        session = SessionLocal()
        
        # Находим или создаем компанию
        company = None
        if data.get('Company_name'):
            company = session.query(Company).filter(Company.company_name == data['Company_name']).first()
            if not company:
                company = Company(
                    company_name=data['Company_name'],
                    company_address='',
                    company_website=''
                )
                session.add(company)
                session.flush()  # Получаем ID компании
        
        # Создаем визитку
        card_data = {k: v for k, v in data.items() if k != 'Company_name'}
        card = BusinessCard(**card_data)
        if company:
            card.company_id = company.id
        
        session.add(card)
        session.commit()
        card_id = card.id
        company_id = company.id if company else None
        session.close()
        
        orm_query = f"card = BusinessCard(full_name='{data['full_name']}', status='{data['status']}', company_id={company_id})\nsession.add(card)\nsession.commit()"
        sql_text.delete(1.0, tk.END)
        sql_text.insert(tk.END, orm_query)
        
        sqlalchemy_code = f"company = session.query(Company).filter_by(company_name='{data['Company_name']}').first()\nif not company:\n    company = Company(company_name='{data['Company_name']}')\n    session.add(company)\ncard = BusinessCard(**data)\ncard.company = company\nsession.add(card)\nsession.commit()"
        sqlalchemy_text.delete(1.0, tk.END)
        sqlalchemy_text.insert(tk.END, sqlalchemy_code)
        
        messagebox.showinfo("Успех", f"Визитка сохранена в БД с ID: {card_id}")
        load_db_data()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

def delete_record():
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
        return
    
    item = tree.item(selection[0])
    card_id = item['values'][0]
    
    if messagebox.askyesno("Подтверждение", f"Удалить запись ID: {card_id}?"):
        try:
            session = SessionLocal()
            card = session.query(BusinessCard).filter(BusinessCard.id == card_id).first()
            if card:
                session.delete(card)
                session.commit()
            session.close()
            
            orm_query = f"card = session.query(BusinessCard).filter(BusinessCard.id == {card_id}).first()\nsession.delete(card)\nsession.commit()"
            sql_text.delete(1.0, tk.END)
            sql_text.insert(tk.END, orm_query)
            
            sqlalchemy_code = f"card = session.query(BusinessCard).filter(BusinessCard.id == {card_id}).first()\nsession.delete(card)\nsession.commit()"
            sqlalchemy_text.delete(1.0, tk.END)
            sqlalchemy_text.insert(tk.END, sqlalchemy_code)
            
            messagebox.showinfo("Успех", "Запись удалена")
            load_db_data()
            add_new()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить: {str(e)}")

def load_db_data():
    for item in tree.get_children():
        tree.delete(item)
    
    session = SessionLocal()
    try:
        cards = session.query(BusinessCard).outerjoin(Company).all()
        
        orm_query = "cards = session.query(BusinessCard).outerjoin(Company).all()"
        sql_text.delete(1.0, tk.END)
        sql_text.insert(tk.END, orm_query)
        
        sqlalchemy_code = "cards = session.query(BusinessCard).outerjoin(Company).all()"
        sqlalchemy_text.delete(1.0, tk.END)
        sqlalchemy_text.insert(tk.END, sqlalchemy_code)
        
        for card in cards:
            company_name = card.company.company_name if card.company else ""
            tree.insert("", "end", values=(
                card.id,
                card.full_name or "",
                company_name,
                card.phone_number or "",
                card.email or ""
            ))
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
    finally:
        session.close()

def on_tree_select(event):
    selection = tree.selection()
    if selection:
        item = tree.item(selection[0])
        card_id = item['values'][0]
        
        session = SessionLocal()
        card = session.query(BusinessCard).outerjoin(Company).filter(BusinessCard.id == card_id).first()
        
        orm_query = f"card = session.query(BusinessCard).outerjoin(Company).filter(BusinessCard.id == {card_id}).first()"
        sql_text.delete(1.0, tk.END)
        sql_text.insert(tk.END, orm_query)
        
        sqlalchemy_code = f"card = session.query(BusinessCard).outerjoin(Company).filter(BusinessCard.id == {card_id}).first()"
        sqlalchemy_text.delete(1.0, tk.END)
        sqlalchemy_text.insert(tk.END, sqlalchemy_code)
        
        if card:
            entries['full_name'].delete(0, tk.END)
            entries['full_name'].insert(0, card.full_name or "")
            
            entries['status'].delete(0, tk.END)
            entries['status'].insert(0, card.status or "")
            
            entries['Company_name'].delete(0, tk.END)
            company_name = card.company.company_name if card.company else ""
            entries['Company_name'].insert(0, company_name)
            
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
root.geometry("1200x700")

# Левый фрейм - данные из БД
left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

tk.Label(left_frame, text="База данных визиток", font=("Arial", 14, "bold")).pack(pady=5)

# Таблица
columns = ("ID", "Имя", "Компания", "Телефон", "Email")
tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill="both", expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)

# ORM запрос
tk.Label(left_frame, text="ORM запрос:", font=("Arial", 10, "bold")).pack(pady=(10,0))
sql_text = scrolledtext.ScrolledText(left_frame, height=3, font=("Courier", 9))
sql_text.pack(fill="x", pady=2)

# SQLAlchemy код
tk.Label(left_frame, text="SQLAlchemy код:", font=("Arial", 10, "bold")).pack(pady=(5,0))
sqlalchemy_text = scrolledtext.ScrolledText(left_frame, height=4, font=("Courier", 9))
sqlalchemy_text.pack(fill="x", pady=2)

# Правый фрейм - добавление визиток
right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

tk.Label(right_frame, text="Управление визитками", font=("Arial", 14, "bold")).pack(pady=5)

# Кнопки управления
button_frame = tk.Frame(right_frame)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Добавить нового", command=add_new, font=("Arial", 10))
add_button.pack(side="left", padx=5)

save_button = tk.Button(button_frame, text="Сохранить", command=save_to_db, font=("Arial", 10))
save_button.pack(side="left", padx=5)

delete_button = tk.Button(button_frame, text="Удалить", command=delete_record, font=("Arial", 10))
delete_button.pack(side="left", padx=5)

# Кнопка распознавания
recognize_button = tk.Button(right_frame, text="Выбрать изображение", command=select_and_recognize, font=("Arial", 12))
recognize_button.pack(pady=10)

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
    frame.pack(pady=3, padx=20, fill="x")
    
    label = tk.Label(frame, text=label_text, width=12, anchor="w")
    label.pack(side="left")
    
    entry = tk.Entry(frame, width=30)
    entry.pack(side="right", fill="x", expand=True)
    
    entries[field_name] = entry

# Загрузка данных при запуске
load_db_data()

root.mainloop()