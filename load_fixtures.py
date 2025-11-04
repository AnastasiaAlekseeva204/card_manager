import json
from card_service import CardService

def load_fixtures_from_json():
    with open('fixtures.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    card_service = CardService()
    
    for employee in data['employees']:
        card_service.save_card(employee)
    
    print(f"Загружено {len(data['employees'])} сотрудников из {len(data['companies'])} компаний")

if __name__ == "__main__":
    load_fixtures_from_json()