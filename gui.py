import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import json
from database import SessionLocal, BusinessCard, Company
from recognition import recognize_text_from_image

class BusinessCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление визитными картами")
        self.root.geometry("1200x700")
        
        self.setup_ui()
        self.load_db_data()
    
    def setup_ui(self):
        # Левый фрейм - данные из БД
        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(left_frame, text="База данных визиток", font=("Arial", 14, "bold")).pack(pady=5)

        # Таблица
        columns = ("ID", "Имя", "Компания", "Телефон", "Email")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # ORM запрос
        tk.Label(left_frame, text="ORM запрос:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.sql_text = scrolledtext.ScrolledText(left_frame, height=3, font=("Courier", 9))
        self.sql_text.pack(fill="x", pady=2)

        # SQLAlchemy код
        tk.Label(left_frame, text="SQLAlchemy код:", font=("Arial", 10, "bold")).pack(pady=(5,0))
        self.sqlalchemy_text = scrolledtext.ScrolledText(left_frame, height=4, font=("Courier", 9))
        self.sqlalchemy_text.pack(fill="x", pady=2)

        # Правый фрейм - добавление визиток
        right_frame = tk.Frame(self.root)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(right_frame, text="Управление визитками", font=("Arial", 14, "bold")).pack(pady=5)

        # Кнопки управления
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=10)

        add_button = tk.Button(button_frame, text="Добавить нового", command=self.add_new, font=("Arial", 10))
        add_button.pack(side="left", padx=5)

        save_button = tk.Button(button_frame, text="Сохранить", command=self.save_to_db, font=("Arial", 10))
        save_button.pack(side="left", padx=5)

        delete_button = tk.Button(button_frame, text="Удалить", command=self.delete_record, font=("Arial", 10))
        delete_button.pack(side="left", padx=5)
        
        backup_button = tk.Button(button_frame, text="Бэкап", command=self.backup_db, font=("Arial", 10))
        backup_button.pack(side="left", padx=5)

        # Кнопка распознавания
        recognize_button = tk.Button(right_frame, text="Выбрать изображение", command=self.select_and_recognize, font=("Arial", 12))
        recognize_button.pack(pady=10)

        self.entries = {}
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
            
            self.entries[field_name] = entry

    def select_and_recognize(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if file_path:
            for entry in self.entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, "Распознавание...")
            self.root.update()
            
            try:
                result = recognize_text_from_image(file_path)
                data = json.loads(result)
                
                for field_name, entry in self.entries.items():
                    if field_name == 'Company_name':
                        entry.delete(0, tk.END)
                        entry.insert(0, data.get('Company_name', ''))
                    else:
                        entry.delete(0, tk.END)
                        entry.insert(0, data.get(field_name, ''))
                
            except Exception as e:
                for entry in self.entries.values():
                    entry.delete(0, tk.END)
                    entry.insert(0, f"Ошибка: {str(e)}")

    def add_new(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.sql_text.delete(1.0, tk.END)
        self.sql_text.insert(tk.END, "# Новая запись")
        self.sqlalchemy_text.delete(1.0, tk.END)
        self.sqlalchemy_text.insert(tk.END, "# Очистка формы")

    def save_to_db(self):
        data = {}
        for field_name, entry in self.entries.items():
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
            self.sql_text.delete(1.0, tk.END)
            self.sql_text.insert(tk.END, orm_query)
            
            sqlalchemy_code = f"company = session.query(Company).filter_by(company_name='{data['Company_name']}').first()\nif not company:\n    company = Company(company_name='{data['Company_name']}')\n    session.add(company)\ncard = BusinessCard(**data)\ncard.company = company\nsession.add(card)\nsession.commit()"
            self.sqlalchemy_text.delete(1.0, tk.END)
            self.sqlalchemy_text.insert(tk.END, sqlalchemy_code)
            
            messagebox.showinfo("Успех", f"Визитка сохранена в БД с ID: {card_id}")
            self.load_db_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

    def backup_db(self):
        try:
            session = SessionLocal()
            cards = session.query(BusinessCard).all()
            
            backup_data = []
            for card in cards:
                backup_data.append({
                    'id': card.id,
                    'full_name': card.full_name,
                    'status': card.status,
                    'Company_name': card.Company_name,
                    'phone_number': card.phone_number,
                    'adress': card.adress,
                    'email': card.email,
                    'website': card.website,
                    'additional_info': card.additional_info
                })
            
            session.close()
            
            from datetime import datetime
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Успех", f"Бэкап сохранен: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать бэкап: {str(e)}")
    
    def delete_record(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        item = self.tree.item(selection[0])
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
                self.sql_text.delete(1.0, tk.END)
                self.sql_text.insert(tk.END, orm_query)
                
                sqlalchemy_code = f"card = session.query(BusinessCard).filter(BusinessCard.id == {card_id}).first()\nsession.delete(card)\nsession.commit()"
                self.sqlalchemy_text.delete(1.0, tk.END)
                self.sqlalchemy_text.insert(tk.END, sqlalchemy_code)
                
                messagebox.showinfo("Успех", "Запись удалена")
                self.load_db_data()
                self.add_new()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {str(e)}")

    def load_db_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        session = SessionLocal()
        try:
            cards = session.query(BusinessCard).outerjoin(Company).all()
            
            orm_query = "cards = session.query(BusinessCard).outerjoin(Company).all()"
            self.sql_text.delete(1.0, tk.END)
            self.sql_text.insert(tk.END, orm_query)
            
            sqlalchemy_code = "cards = session.query(BusinessCard).outerjoin(Company).all()"
            self.sqlalchemy_text.delete(1.0, tk.END)
            self.sqlalchemy_text.insert(tk.END, sqlalchemy_code)
            
            for card in cards:
                company_name = card.company.company_name if card.company else ""
                self.tree.insert("", "end", values=(
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

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            card_id = item['values'][0]
            
            session = SessionLocal()
            card = session.query(BusinessCard).outerjoin(Company).filter(BusinessCard.id == card_id).first()
            
            orm_query = f"card = session.query(BusinessCard).outerjoin(Company).filter(BusinessCard.id == {card_id}).first()"
            self.sql_text.delete(1.0, tk.END)
            self.sql_text.insert(tk.END, orm_query)
            
            sqlalchemy_code = f"card = session.query(BusinessCard).outerjoin(Company).filter(BusinessCard.id == {card_id}).first()"
            self.sqlalchemy_text.delete(1.0, tk.END)
            self.sqlalchemy_text.insert(tk.END, sqlalchemy_code)
            
            if card:
                self.entries['full_name'].delete(0, tk.END)
                self.entries['full_name'].insert(0, card.full_name or "")
                
                self.entries['status'].delete(0, tk.END)
                self.entries['status'].insert(0, card.status or "")
                
                self.entries['Company_name'].delete(0, tk.END)
                company_name = card.company.company_name if card.company else ""
                self.entries['Company_name'].insert(0, company_name)
                
                self.entries['phone_number'].delete(0, tk.END)
                self.entries['phone_number'].insert(0, card.phone_number or "")
                
                self.entries['adress'].delete(0, tk.END)
                self.entries['adress'].insert(0, card.adress or "")
                
                self.entries['email'].delete(0, tk.END)
                self.entries['email'].insert(0, card.email or "")
                
                self.entries['website'].delete(0, tk.END)
                self.entries['website'].insert(0, card.website or "")
                
                self.entries['additional_info'].delete(0, tk.END)
                self.entries['additional_info'].insert(0, card.additional_info or "")
            
            session.close()

def main():
    root = tk.Tk()
    app = BusinessCardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()