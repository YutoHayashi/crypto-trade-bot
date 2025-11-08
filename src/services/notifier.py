import json

import requests


class Notifier:
    def notify(self, message: str):
        """
        Notify the user with a message.
        This method is a placeholder for the actual notification logic.
        :param message: The message to notify the user with.
        """
        path = "/message/push"
        data = json.dumps({
            "to": self._line_messaging_api_destination_user_id,
            "messages": [{
                "type": "text",
                "text": message,
                "wrap": True,
            }]
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._line_messaging_api_channel_token}",
        }
        response = requests.post(self.line_messaging_api_base_url + path, data=data, headers=headers)
        return response.json()
    
    def __init__(self,
                 line_messaging_api_base_url: str,
                 line_messaging_api_channel_token: str,
                 line_messaging_api_destination_user_id: str):
        """
        Initialize the NotificationService.
        This method can be extended to set up any necessary configurations or dependencies.
        """
        self.line_messaging_api_base_url = line_messaging_api_base_url
        self._line_messaging_api_channel_token = line_messaging_api_channel_token
        self._line_messaging_api_destination_user_id = line_messaging_api_destination_user_id