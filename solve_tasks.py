"""
Решение задач для БД визиток с использованием SQLAlchemy
Подключение к PostgreSQL в Docker контейнере
"""

from sqlalchemy import create_engine, func, or_, desc
from sqlalchemy.orm import sessionmaker
from database_postgres import BusinessCard, Company, Base

# Подключение к БД
DATABASE_URL = "postgresql://user:password@localhost:5437/business_cards"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """Получить сессию БД"""
    return SessionLocal()

def task_example():
    """Пример задачи: Получить всех сотрудников компании 'ООО Технологии'"""
    session = get_session()
    try:
        result = session.query(BusinessCard.full_name, BusinessCard.status, BusinessCard.phone_number, BusinessCard.email)\
            .join(Company)\
            .filter(Company.company_name == 'ООО Технологии').all()
        return result
    finally:
        session.close()

if __name__ == "__main__":
    # Проверка подключения
    try:
        session = get_session()
        count = session.query(func.count(BusinessCard.id)).scalar()
        print(f"Подключение успешно! В БД {count} сотрудников")
        session.close()
        
        # Запуск примера задачи
        result = task_example()
        print("\nПример задачи - сотрудники ООО Технологии:")
        for row in result:
            print(f"  {row}")
            
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        print("Убедитесь что Docker контейнер запущен: docker-compose up -d")