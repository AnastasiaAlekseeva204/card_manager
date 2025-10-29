from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///business_cards.sqlite')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    company_address = Column(String)
    company_website = Column(String)
    
    business_cards = relationship("BusinessCard", back_populates="company")

class BusinessCard(Base):
    __tablename__ = 'business_cards'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    status = Column(String)
    phone_number = Column(String)
    adress = Column(String)
    email = Column(String)
    website = Column(String)
    additional_info = Column(String)
    
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="business_cards")

Base.metadata.create_all(bind=engine)

def save_business_card(data):
    session = SessionLocal()
    
    company = None
    if data.get('Company_name'):
        company = session.query(Company).filter(Company.company_name == data['Company_name']).first()
        if not company:
            company = Company(
                company_name=data.get('Company_name', ''),
                company_address=data.get('adress', ''),
                company_website=data.get('website', '')
            )
            session.add(company)
            session.commit()
    
    card_data = {k: v for k, v in data.items() if k != 'Company_name'}
    card = BusinessCard(**card_data)
    if company:
        card.company_id = company.id
    
    session.add(card)
    session.commit()
    card_id = card.id
    session.close()
    return card_id