from __future__ import annotations
import requests
import json
from typing import Union
from .objects import Message
from .errors import RatelimitError, WebhookError, NotFound, GeneralAPIError, BadRequest

class Webhook:
    """A webhook on Discord that allows you to send messages"""
    def __init__(self, webhook_url: str):
        if '?wait=true' in webhook_url:
            webhook_url = webhook_url.replace('?wait=true', '')
        elif '&wait=true' in webhook_url:
            webhook_url = webhook_url.replace('&wait=true', '')

        self.webhook = webhook_url
        self.info: WebhookInfo | None = None
        self.session = requests.Session()
        self.fetch_metadata()

    def req_webhook(
            self,
            json_data: dict | None = None,
            type: str = 'get',
            data: dict | None = None,
            files: dict | None = None,
            msg_id: str | None = None
        ) -> requests.Response:

        if msg_id and type in ('patch', 'delete'):
            url = f'{self.webhook}/messages/{msg_id}'
        else:
            url = self.webhook

        if type in ('post', 'patch', 'files', 'delete'):
            url = f'{url}?wait=true'

        try:
            if type == 'get':
                response = self.session.get(url)
            elif type == 'post':
                if files is not None:
                    response = self.session.post(url, files=files)
                else:
                    response = self.session.post(url, json=json_data)
            elif type == 'patch':
                if files is not None:
                    response = self.session.post(url, files=files)
                else:
                    response = self.session.post(url, json=json_data)
            elif type == 'delete':
                response = self.session.delete(url)
            else:
                raise ValueError('No type for that?')
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
        
    def fetch_metadata(self):
        """Fetches the metadata of the webhook"""
        response = self.req_webhook(type='get')
        data = response.json()

        self.info = WebhookInfo(data)

    def send(self, message: Message, username: str | None = None, avatar_url: str | None = None):
        """_Sends a message with the webhook_

        Args:
            message (Message): _The message object to use_
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

        if message.files:
            files_payload = message.get_files_payload()
            form_data = {'payload_json': (None, json.dumps(payload), 'application/json')}
            form_data.update(files_payload)

            try:
                return self.req_webhook(type='post', json_data=payload, files=form_data)
            finally:
                for file_obj in message.files:
                    file_obj.close()
        else:
            return self.req_webhook(type='post', json_data=payload)
        
    def edit(self, message_id: str, new_msg: Message | str):
        if isinstance(new_msg, str):
            new_msg = Message(content=new_msg)

        payload = new_msg.to_dict()
        return self.req_webhook(type='patch', json_data=payload, msg_id=message_id)
    
    def delete(self, message_id: str):
        return self.req_webhook(type='delete', msg_id=message_id)

class WebhookInfo:
    """The info of the webhook itself (name, channel, etc.)"""
    def __init__(self, data: dict):
        self.id: str = data.get('id', '')
        self.name: str = data.get('name', '')
        self.avatar: str = data.get('avatar', '')
        self.channel_id: str = data.get('channel_id', '')
        self.guild_id: str = data.get('guild_id', '')
        self.id: str = data.get('id', '')
        self.token: str = data.get('token', '')
        self.url: str = data.get('url', '')