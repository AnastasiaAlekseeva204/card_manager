from database_postgres import SessionLocal, BusinessCard, Company

def create_fixtures():
    session = SessionLocal()
    
    # Создаем компании
    companies = [
        Company(company_name="ООО Технологии", company_address="Москва, ул. Ленина 1", company_website="tech.ru"),
        Company(company_name="ИП Иванов", company_address="СПб, пр. Мира 15", company_website="ivanov.com"),
        Company(company_name="АО Развитие", company_address="Казань, ул. Победы 7", company_website="razvitie.org")
    ]
    
    for company in companies:
        session.add(company)
    session.flush()
    
    # Создаем сотрудников
    employees = [
        # ООО Технологии (5 сотрудников)
        {"full_name": "Петров Иван", "status": "Директор", "phone_number": "+7-900-123-45-67", "email": "petrov@tech.ru", "company_id": companies[0].id},
        {"full_name": "Сидорова Анна", "status": "Менеджер", "phone_number": "+7-900-234-56-78", "email": "sidorova@tech.ru", "company_id": companies[0].id},
        {"full_name": "Козлов Петр", "status": "Программист", "phone_number": "+7-900-345-67-89", "email": "kozlov@tech.ru", "company_id": companies[0].id},
        {"full_name": "Морозова Елена", "status": "Дизайнер", "phone_number": "+7-900-456-78-90", "email": "morozova@tech.ru", "company_id": companies[0].id},
        {"full_name": "Волков Сергей", "status": "Тестировщик", "phone_number": "+7-900-567-89-01", "email": "volkov@tech.ru", "company_id": companies[0].id},
        
        # ИП Иванов (3 сотрудника)
        {"full_name": "Иванов Михаил", "status": "Предприниматель", "phone_number": "+7-911-123-45-67", "email": "m.ivanov@ivanov.com", "company_id": companies[1].id},
        {"full_name": "Смирнова Ольга", "status": "Помощник", "phone_number": "+7-911-234-56-78", "email": "smirnova@ivanov.com", "company_id": companies[1].id},
        {"full_name": "Попов Андрей", "status": "Консультант", "phone_number": "+7-911-345-67-89", "email": "popov@ivanov.com", "company_id": companies[1].id},
        
        # АО Развитие (2 сотрудника)
        {"full_name": "Новиков Алексей", "status": "Генеральный директор", "phone_number": "+7-987-123-45-67", "email": "novikov@razvitie.org", "company_id": companies[2].id},
        {"full_name": "Федорова Мария", "status": "Секретарь", "phone_number": "+7-987-234-56-78", "email": "fedorova@razvitie.org", "company_id": companies[2].id}
    ]
    
    for emp_data in employees:
        card = BusinessCard(**emp_data)
        session.add(card)
    
    session.commit()
    session.close()
    print("Фикстуры созданы: 3 компании, 10 сотрудников")

if __name__ == "__main__":
    create_fixtures()