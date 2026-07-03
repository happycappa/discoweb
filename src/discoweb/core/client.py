from __future__ import annotations
import requests
from .objects import Message
from .errors import RatelimitError, WebhookError, NotFound, GeneralAPIError, BadRequest

class Webhook:
    """A webhook on Discord that allows you to send messages"""
    def __init__(self, webhook_url: str):
        self.webhook = webhook_url
        self.session = requests.Session()

    def req_webhook(self, get: bool = False, data: dict | None = None) -> requests.Response:
        try:
            response = self.session.get(self.webhook) if get else self.session.post(self.webhook, json=data)
        except requests.RequestException as error:
            raise GeneralAPIError(f'Network error occured: {error}')

        if response.status_code == 400:
            try:
                disc_response = response.json().get('message', 'Bad request error occured, maybe you answered a parameter wrong?')
            except ValueError:
                disc_response = 'Invalid JSON response'
            raise BadRequest(disc_response)
        elif response.status_code == 429:
            raise RatelimitError("You've hit Discord's ratelimit, slow down!")
        
        try:
            response.raise_for_status()
            return response
        except requests.RequestException as HTTPError:
            raise GeneralAPIError(f'HTTP Error occured: {HTTPError}')
        
    def send(self, message: Message, del_after: int | None = None, username: str | None = None, avatar_url: str | None = None):
        """_Sends a message with the webhook_

        Args:
            message (Message): _The message object to use_
            del_after (int | None, optional): _The time (in seconds) before it's deleted_. Defaults to None.
            username (str | None, optional): _The username to use_. Defaults to None.
            avatar_url (str | None, optional): _The image URL of the avatar to use_. Defaults to None.
        """
        if isinstance(message, str):
            payload = Message(content=message)

        payload = message.to_dict()

        if username is not None:
            payload['username'] = username
        if avatar_url is not None:
            payload['avatar_url'] = avatar_url

        self.req_webhook(False, payload)