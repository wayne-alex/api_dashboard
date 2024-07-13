import json
import requests

class Client:
    def __init__(self, acc_sid, username):
        self.username = username
        self.acc_sid = acc_sid

    def generate_token(self):
        try:
            url = "http://127.0.0.1:8000/generate_token/"
            data = {'username': self.username, 'acc_sid': self.acc_sid}
            headers = {'Content-Type': 'application/json'}

            response = requests.post(url, data=json.dumps(data), headers=headers)

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def whatsapp_api(self, token, to, message):
        try:
            payload = {'token': token, 'to': to, 'message_body': message}
            url = "http://api.services.com/whatsapp"

            response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}

    def chatgpt(self, token, prompt):
        try:
            payload = {'token': token, 'prompt': prompt}
            url = "http://127.0.0.1:8000/chatgpt_api/"

            response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": {"code": response.status_code, "message": response.text}}
        except Exception as e:
            return {"success": False, "error": {"message": str(e)}}
