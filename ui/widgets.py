import tkinter as tk
from tkinter import ttk, scrolledtext

class CardForm:
    def __init__(self, parent):
        self.entries = {}
        self.create_form(parent)
    
    def create_form(self, parent):
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
            frame = tk.Frame(parent)
            frame.pack(pady=3, padx=20, fill="x")
            
            label = tk.Label(frame, text=label_text, width=12, anchor="w")
            label.pack(side="left")
            
            entry = tk.Entry(frame, width=30)
            entry.pack(side="right", fill="x", expand=True)
            
            self.entries[field_name] = entry
    
    def get_data(self):
        return {field: entry.get() for field, entry in self.entries.items()}
    
    def set_data(self, data):
        for field, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, data.get(field, ""))
    
    def clear(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

class CardTable:
    def __init__(self, parent):
        self.tree = self.create_table(parent)
    
    def create_table(self, parent):
        columns = ("ID", "Имя", "Компания", "Телефон", "Email")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        tree.heading("ID", text="ID")
        tree.column("ID", width=50)
        
        for col in columns[1:]:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        tree.pack(fill="both", expand=True)
        return tree
    
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_card(self, card):
        company_name = card.company.company_name if card.company else ""
        self.tree.insert("", "end", values=(
            card.id,
            card.full_name or "",
            company_name,
            card.phone_number or "",
            card.email or ""
        ))

class SQLDisplay:
    def __init__(self, parent):
        self.sql_text = self.create_sql_display(parent, "ORM запрос:", 3)
        self.sqlalchemy_text = self.create_sql_display(parent, "SQLAlchemy код:", 4)
    
    def create_sql_display(self, parent, label, height):
        tk.Label(parent, text=label, font=("Arial", 10, "bold")).pack(pady=(10,0))
        text_widget = scrolledtext.ScrolledText(parent, height=height, font=("Courier", 9))
        text_widget.pack(fill="x", pady=2)
        return text_widget
    
    def update_sql(self, query):
        self.sql_text.delete(1.0, tk.END)
        self.sql_text.insert(tk.END, query)
    
    def update_sqlalchemy(self, code):
        self.sqlalchemy_text.delete(1.0, tk.END)
        self.sqlalchemy_text.insert(tk.END, code)