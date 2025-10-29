from database import SessionLocal, BusinessCard

session = SessionLocal()

# Проверяем все записи
cards = session.query(BusinessCard).all()
print(f"Всего записей: {len(cards)}")

for card in cards:
    print(f"ID: {card.id}")
    print(f"Имя: {card.full_name}")
    print(f"Компания: {card.Company_name}")
    print(f"Email: {card.email}")
    print("-" * 30)

session.close()