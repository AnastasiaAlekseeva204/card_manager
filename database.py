from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///business_cards.sqlite')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class BusinessCard(Base):
    __tablename__ = 'business_cards'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    status = Column(String)
    Company_name = Column(String)
    phone_number = Column(String)
    adress = Column(String)
    email = Column(String)
    website = Column(String)
    additional_info = Column(String)

Base.metadata.create_all(bind=engine)

def save_business_card(data):
    session = SessionLocal()
    card = BusinessCard(**data)
    session.add(card)
    session.commit()
    session.close()
    return card.id