import json
from database import SessionLocal, Company, BusinessCard

def load_fixtures():
    with open('fixtures.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    session = SessionLocal()
    
    '''Очищаем таблицы
    session.query(BusinessCard).delete()
    session.query(Company).delete()
    session.commit()'''
    
    # Загружаем компании
    companies = {}
    for company_data in data['companies']:
        company = Company(**company_data)
        session.add(company)
        session.flush()
        companies[company_data['company_name']] = company.id
    
    # Загружаем визитки
    for card_data in data['business_cards']:
        company_name = card_data.pop('company_name')
        card = BusinessCard(**card_data)
        card.company_id = companies[company_name]
        session.add(card)
    
    session.commit()
    session.close()
    print("Фикстуры загружены успешно!")

if __name__ == "__main__":
    load_fixtures()