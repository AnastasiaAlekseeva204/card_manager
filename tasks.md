# Задачи для БД визиток

## Простые задачи

## 1. Получить всех сотрудников компании "ООО Технологии"

**SQL:**
```sql
SELECT bc.full_name, bc.status, bc.phone_number, bc.email
FROM business_cards bc
JOIN companies c ON bc.company_id = c.id
WHERE c.company_name = 'ООО Технологии';
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.status, BusinessCard.phone_number, BusinessCard.email)\
    .join(Company)\
    .filter(Company.company_name == 'ООО Технологии').all()
```

## 2. Найти всех директоров

**SQL:**
```sql
SELECT full_name, phone_number, email
FROM business_cards
WHERE status LIKE '%директор%' OR status LIKE '%Директор%';
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.phone_number, BusinessCard.email)\
    .filter(BusinessCard.status.ilike('%директор%')).all()
```

## 3. Получить список всех компаний

**SQL:**
```sql
SELECT company_name, company_address, company_website
FROM companies
ORDER BY company_name;
```

**SQLAlchemy:**
```python
result = session.query(Company.company_name, Company.company_address, Company.company_website)\
    .order_by(Company.company_name).all()
```

## 4. Найти сотрудников с именем "Иван"

**SQL:**
```sql
SELECT full_name, status, c.company_name
FROM business_cards bc
LEFT JOIN companies c ON bc.company_id = c.id
WHERE full_name LIKE '%Иван%';
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.status, Company.company_name)\
    .outerjoin(Company)\
    .filter(BusinessCard.full_name.like('%Иван%')).all()
```

## 5. Подсчитать общее количество сотрудников

**SQL:**
```sql
SELECT COUNT(*) as total_employees
FROM business_cards;
```

**SQLAlchemy:**
```python
from sqlalchemy import func
result = session.query(func.count(BusinessCard.id)).scalar()
```

## 6. Найти сотрудников с gmail почтой

**SQL:**
```sql
SELECT full_name, email, status
FROM business_cards
WHERE email LIKE '%@gmail.com';
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.email, BusinessCard.status)\
    .filter(BusinessCard.email.like('%@gmail.com')).all()
```

## 7. Получить всех сотрудников без компании

**SQL:**
```sql
SELECT full_name, status, phone_number, email
FROM business_cards
WHERE company_id IS NULL;
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.status, BusinessCard.phone_number, BusinessCard.email)\
    .filter(BusinessCard.company_id.is_(None)).all()
```

## 8. Найти компанию по адресу в Москве

**SQL:**
```sql
SELECT company_name, company_address, company_website
FROM companies
WHERE company_address LIKE '%Москва%';
```

**SQLAlchemy:**
```python
result = session.query(Company.company_name, Company.company_address, Company.company_website)\
    .filter(Company.company_address.like('%Москва%')).all()
```

## 9. Получить первых 5 сотрудников по алфавиту

**SQL:**
```sql
SELECT full_name, status, phone_number
FROM business_cards
ORDER BY full_name
LIMIT 5;
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.status, BusinessCard.phone_number)\
    .order_by(BusinessCard.full_name)\
    .limit(5).all()
```

## 10. Найти сотрудников с заполненным сайтом

**SQL:**
```sql
SELECT full_name, website, c.company_name
FROM business_cards bc
LEFT JOIN companies c ON bc.company_id = c.id
WHERE bc.website IS NOT NULL AND bc.website != '';
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.website, Company.company_name)\
    .outerjoin(Company)\
    .filter(BusinessCard.website.isnot(None), BusinessCard.website != '').all()
```

## Задачи средней сложности

## 11. Найти все компании с количеством сотрудников больше 3

**SQL:**
```sql
SELECT c.company_name, COUNT(bc.id) as employee_count
FROM companies c
LEFT JOIN business_cards bc ON c.id = bc.company_id
GROUP BY c.id, c.company_name
HAVING COUNT(bc.id) > 3;
```

**SQLAlchemy:**
```python
from sqlalchemy import func
result = session.query(Company.company_name, func.count(BusinessCard.id).label('employee_count'))\
    .outerjoin(BusinessCard)\
    .group_by(Company.id, Company.company_name)\
    .having(func.count(BusinessCard.id) > 3).all()
```

## 2. Найти сотрудников без указанного email

**SQL:**
```sql
SELECT full_name, status, company_name
FROM business_cards bc
LEFT JOIN companies c ON bc.company_id = c.id
WHERE bc.email IS NULL OR bc.email = '';
```

**SQLAlchemy:**
```python
from sqlalchemy import or_
result = session.query(BusinessCard.full_name, BusinessCard.status, Company.company_name)\
    .outerjoin(Company)\
    .filter(or_(BusinessCard.email.is_(None), BusinessCard.email == '')).all()
```

## 3. Получить топ-3 компании по количеству сотрудников

**SQL:**
```sql
SELECT c.company_name, COUNT(bc.id) as employee_count
FROM companies c
LEFT JOIN business_cards bc ON c.id = bc.company_id
GROUP BY c.id, c.company_name
ORDER BY employee_count DESC
LIMIT 3;
```

**SQLAlchemy:**
```python
result = session.query(Company.company_name, func.count(BusinessCard.id).label('employee_count'))\
    .outerjoin(BusinessCard)\
    .group_by(Company.id, Company.company_name)\
    .order_by(func.count(BusinessCard.id).desc())\
    .limit(3).all()
```

## 4. Найти дублирующиеся email адреса

**SQL:**
```sql
SELECT email, COUNT(*) as count
FROM business_cards
WHERE email IS NOT NULL AND email != ''
GROUP BY email
HAVING COUNT(*) > 1;
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.email, func.count().label('count'))\
    .filter(BusinessCard.email.isnot(None), BusinessCard.email != '')\
    .group_by(BusinessCard.email)\
    .having(func.count() > 1).all()
```

## 5. Найти компании без сотрудников

**SQL:**
```sql
SELECT c.company_name, c.company_address
FROM companies c
LEFT JOIN business_cards bc ON c.id = bc.company_id
WHERE bc.id IS NULL;
```

**SQLAlchemy:**
```python
result = session.query(Company.company_name, Company.company_address)\
    .outerjoin(BusinessCard)\
    .filter(BusinessCard.id.is_(None)).all()
```

## 6. Получить статистику по должностям

**SQL:**
```sql
SELECT status, COUNT(*) as count, 
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM business_cards), 2) as percentage
FROM business_cards
WHERE status IS NOT NULL AND status != ''
GROUP BY status
ORDER BY count DESC;
```

**SQLAlchemy:**
```python
total_count = session.query(BusinessCard).count()
result = session.query(
    BusinessCard.status,
    func.count().label('count'),
    (func.count() * 100.0 / total_count).label('percentage')
)\
.filter(BusinessCard.status.isnot(None), BusinessCard.status != '')\
.group_by(BusinessCard.status)\
.order_by(func.count().desc()).all()
```

## 7. Найти сотрудников с телефонами определенного оператора (+7-900)

**SQL:**
```sql
SELECT full_name, phone_number, c.company_name
FROM business_cards bc
LEFT JOIN companies c ON bc.company_id = c.id
WHERE phone_number LIKE '+7-900%';
```

**SQLAlchemy:**
```python
result = session.query(BusinessCard.full_name, BusinessCard.phone_number, Company.company_name)\
    .outerjoin(Company)\
    .filter(BusinessCard.phone_number.like('+7-900%')).all()
```

## 8. Получить полную информацию о компании с наибольшим количеством сотрудников

**SQL:**
```sql
WITH company_stats AS (
    SELECT c.*, COUNT(bc.id) as employee_count
    FROM companies c
    LEFT JOIN business_cards bc ON c.id = bc.company_id
    GROUP BY c.id
)
SELECT * FROM company_stats
WHERE employee_count = (SELECT MAX(employee_count) FROM company_stats);
```

**SQLAlchemy:**
```python
from sqlalchemy import desc
subq = session.query(
    Company.id,
    func.count(BusinessCard.id).label('employee_count')
)\
.outerjoin(BusinessCard)\
.group_by(Company.id)\
.subquery()

max_count = session.query(func.max(subq.c.employee_count)).scalar()

result = session.query(Company)\
    .join(subq, Company.id == subq.c.id)\
    .filter(subq.c.employee_count == max_count).first()
```

## 9. Найти сотрудников, у которых домен email совпадает с доменом сайта компании

**SQL:**
```sql
SELECT bc.full_name, bc.email, c.company_name, c.company_website
FROM business_cards bc
JOIN companies c ON bc.company_id = c.id
WHERE bc.email IS NOT NULL 
  AND c.company_website IS NOT NULL
  AND SUBSTRING(bc.email FROM '@(.*)') = c.company_website;
```

**SQLAlchemy:**
```python
from sqlalchemy import func
result = session.query(BusinessCard.full_name, BusinessCard.email, Company.company_name, Company.company_website)\
    .join(Company)\
    .filter(
        BusinessCard.email.isnot(None),
        Company.company_website.isnot(None),
        func.substring(BusinessCard.email, '@(.*)') == Company.company_website
    ).all()
```

## 10. Получить среднее количество сотрудников на компанию и список компаний выше среднего

**SQL:**
```sql
WITH company_counts AS (
    SELECT c.company_name, COUNT(bc.id) as employee_count
    FROM companies c
    LEFT JOIN business_cards bc ON c.id = bc.company_id
    GROUP BY c.id, c.company_name
),
avg_count AS (
    SELECT AVG(employee_count) as avg_employees
    FROM company_counts
)
SELECT cc.company_name, cc.employee_count, ac.avg_employees
FROM company_counts cc, avg_count ac
WHERE cc.employee_count > ac.avg_employees
ORDER BY cc.employee_count DESC;
```

**SQLAlchemy:**
```python
# Подзапрос для подсчета сотрудников по компаниям
company_counts = session.query(
    Company.company_name,
    func.count(BusinessCard.id).label('employee_count')
)\
.outerjoin(BusinessCard)\
.group_by(Company.id, Company.company_name)\
.subquery()

# Средний показатель
avg_employees = session.query(func.avg(company_counts.c.employee_count)).scalar()

# Компании выше среднего
result = session.query(company_counts.c.company_name, company_counts.c.employee_count)\
    .filter(company_counts.c.employee_count > avg_employees)\
    .order_by(company_counts.c.employee_count.desc()).all()
```