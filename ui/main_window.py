import tkinter as tk
from tkinter import filedialog, messagebox
import json
from datetime import datetime
from widgets import CardForm, CardTable, SQLDisplay
from ocr_service import OCRService
from card_service import CardService

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.ocr_service = OCRService()
        self.card_service = CardService()
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Управление визитными картами")
        self.root.geometry("1200x700")
        
        # Левый фрейм
        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(left_frame, text="База данных визиток", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.table = CardTable(left_frame)
        self.table.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.sql_display = SQLDisplay(left_frame)
        
        # Правый фрейм
        right_frame = tk.Frame(self.root)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(right_frame, text="Управление визитками", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Кнопки
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Добавить нового", command=self.add_new).pack(side="left", padx=5)
        tk.Button(button_frame, text="Сохранить", command=self.save_to_db).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_record).pack(side="left", padx=5)
        tk.Button(button_frame, text="Сделать бекап", command=self.backup_data).pack(side="left", padx=5)
        
        tk.Button(right_frame, text="Выбрать изображение", command=self.select_and_recognize).pack(pady=10)
        
        self.form = CardForm(right_frame)
        
        # Загружаем данные при запуске
        self.load_db_data()
    
    def select_and_recognize(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if file_path:
            self.form.clear()
            for entry in self.form.entries.values():
                entry.insert(0, "Распознавание...")
            self.root.update()
            
            try:
                data = self.ocr_service.recognize_business_card(file_path)
                self.form.set_data(data)
            except Exception as e:
                self.form.clear()
                for entry in self.form.entries.values():
                    entry.insert(0, f"Ошибка: {str(e)}")
    
    def add_new(self):
        self.form.clear()
        self.sql_display.update_sql("# Новая запись")
        self.sql_display.update_sqlalchemy("# Очистка формы")
    
    def save_to_db(self):
        try:
            data = self.form.get_data()
            card_id = self.card_service.save_card(data)
            
            orm_query = f"card = BusinessCard(**data)\nsession.add(card)\nsession.commit()"
            self.sql_display.update_sql(orm_query)
            self.sql_display.update_sqlalchemy(orm_query)
            
            messagebox.showinfo("Успех", f"Визитка сохранена с ID: {card_id}")
            self.load_db_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def delete_record(self):
        selection = self.table.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        item = self.table.tree.item(selection[0])
        card_id = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить запись ID: {card_id}?"):
            try:
                if self.card_service.delete_card(card_id):
                    messagebox.showinfo("Успех", "Запись удалена")
                    self.load_db_data()
                    self.add_new()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить: {str(e)}")
    
    def load_db_data(self):
        self.table.clear()
        cards = self.card_service.get_all_cards()
        
        for card in cards:
            self.table.add_card(card)
        
        self.sql_display.update_sql("cards = session.query(BusinessCard).outerjoin(Company).all()")
        self.sql_display.update_sqlalchemy("cards = session.query(BusinessCard).outerjoin(Company).all()")
    
    def on_tree_select(self, event):
        selection = self.table.tree.selection()
        if selection:
            item = self.table.tree.item(selection[0])
            card_id = item['values'][0]
            
            card = self.card_service.get_card_by_id(card_id)
            if card:
                data = {
                    'full_name': card.full_name or "",
                    'status': card.status or "",
                    'Company_name': card.company.company_name if card.company else "",
                    'phone_number': card.phone_number or "",
                    'adress': card.adress or "",
                    'email': card.email or "",
                    'website': card.website or "",
                    'additional_info': card.additional_info or ""
                }
                self.form.set_data(data)
    
    def backup_data(self):
        try:
            cards = self.card_service.get_all_cards()
            
            backup_data = {
                "companies": [],
                "employees": []
            }
            
            companies_added = set()
            
            for card in cards:
                # Добавляем компанию если еще не добавляли
                if card.company and card.company.company_name not in companies_added:
                    backup_data["companies"].append({
                        "company_name": card.company.company_name,
                        "company_address": card.company.company_address or "",
                        "company_website": card.company.company_website or ""
                    })
                    companies_added.add(card.company.company_name)
                
                # Добавляем сотрудника
                backup_data["employees"].append({
                    "full_name": card.full_name or "",
                    "status": card.status or "",
                    "phone_number": card.phone_number or "",
                    "email": card.email or "",
                    "adress": card.adress or "",
                    "website": card.website or "",
                    "additional_info": card.additional_info or "",
                    "Company_name": card.company.company_name if card.company else ""
                })
            
            # Сохраняем в файл
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Успех", f"Бекап сохранен: {filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать бекап: {str(e)}")
    
    def run(self):
        self.root.mainloop()