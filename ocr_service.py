import uuid
import json
from dotenv import find_dotenv, load_dotenv
from langchain_gigachat.chat_models import GigaChat
from langchain_core.runnables import RunnableConfig

load_dotenv(find_dotenv())

class OCRService:
    def __init__(self):
        self.model = GigaChat(
            model="GigaChat-2-Max",
            verify_ssl_certs=False,
        )
    
    def recognize_business_card(self, image_path):
        with open(image_path, "rb") as image_file:
            file_uploaded_id = self.model.upload_file(image_file).id_
        
        config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})
        
        message = {
            "role": "user",
            "content": "Распознай визитную карточку и верни JSON с полями: full_name, status, Company_name, phone_number, adress, email, website, additional_info. Ответ только JSON, никакого дополнительного текста.",
            "attachments": [file_uploaded_id]
        }
        
        response = self.model.invoke([message], config=config)
        return json.loads(response.content)