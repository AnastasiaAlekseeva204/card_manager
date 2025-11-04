from database_postgres import SessionLocal, BusinessCard, Company

class CardService:
    def __init__(self):
        pass
    
    def save_card(self, data):
        session = SessionLocal()
        try:
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
                    session.flush()
            
            card_data = {k: v for k, v in data.items() if k != 'Company_name'}
            card = BusinessCard(**card_data)
            if company:
                card.company_id = company.id
            
            session.add(card)
            session.commit()
            return card.id
        finally:
            session.close()
    
    def delete_card(self, card_id):
        session = SessionLocal()
        try:
            card = session.query(BusinessCard).filter(BusinessCard.id == card_id).first()
            if card:
                session.delete(card)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_all_cards(self):
        session = SessionLocal()
        try:
            cards = session.query(BusinessCard).outerjoin(Company).all()
            # Принудительно загружаем связанные данные
            for card in cards:
                if card.company:
                    _ = card.company.company_name
            return cards
        finally:
            session.close()
    
    def get_card_by_id(self, card_id):
        session = SessionLocal()
        try:
            card = session.query(BusinessCard).outerjoin(Company).filter(BusinessCard.id == card_id).first()
            if card and card.company:
                _ = card.company.company_name
            return card
        finally:
            session.close()