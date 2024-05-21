import os
import re
import requests
from dotenv import load_dotenv

# получим переменные окружения из .env
load_dotenv()

class Pachka:
    # получим переменные окружения
    USER_ID = os.environ.get("USER_ID")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
    INPUT_WEBHOOKS_URL = os.environ.get("INPUT_WEBHOOKS_URL")
    API_URL = os.environ.get("API_URL")
    CHAT_ID = os.environ.get("CHAT_ID")

    def send_responce(self, thread_id, content):
        headers = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }

        data = {
            "message": {
                "entity_type": "thread",
                "entity_id": thread_id,
                "content": content,
            }
        }

        post_response = requests.post(f"{self.API_URL}/messages", headers=headers, json=data)
        post_response_json = post_response.json()

        return post_response_json
    
    def create_thread(self, message_id):
        # Определяем заголовки для запроса
        headers = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }

        # Запрос
        post_response = requests.post(f"{self.API_URL}/messages/{message_id}/thread", headers=headers)

        post_response_json = post_response.json()
        thread_id = post_response_json['data'].get('id')

        return thread_id