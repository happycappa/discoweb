from __future__ import annotations
import requests
import json
import aiohttp
from .objects import Message
from .errors import RatelimitError, GeneralAPIError, BadRequest

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

        if type in ('post'):
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
                    response = self.session.patch(url, files=files)
                else:
                    response = self.session.patch(url, json=json_data)
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
        """Sends a message with the webhook"""
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
                response = self.req_webhook(type='post', json_data=payload, files=form_data)
                return response.json()
            finally:
                for file_obj in message.files:
                    file_obj.close()
        else:
            response = self.req_webhook(type='post', json_data=payload)
            return response.json()
        
    def edit(self, message_id: str, new_msg: Message | str):
        """Edits a message from the webhook"""
        if isinstance(new_msg, str):
            new_msg = Message(content=new_msg)

        payload = new_msg.to_dict()
        
        if new_msg.files:
            files_payload = new_msg.get_files_payload()
            form_data = {'payload_json': (None, json.dumps(payload), 'application/json')}
            form_data.update(files_payload)

            try:
                response = self.req_webhook(type='patch', files=form_data, msg_id=message_id)
                return response.json()
            finally:
                for file_obj in new_msg.files:
                    file_obj.close()
        else:
            response = self.req_webhook(type='patch', json_data=payload, msg_id=message_id)
            return response.json()
    
    def delete(self, message_id: str):
        """Deletes a message from the webhook"""
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

class AsyncHook:
    """A async version of the Webhook object for support in modern Discord libraries"""
    def __init__(self, webhook_url: str):
        if '?wait=true' in webhook_url:
            webhook_url = webhook_url.replace('?wait=true', '')
        elif '&wait=true' in webhook_url:
            webhook_url = webhook_url.replace('&wait=true', '')

        self.webhook = webhook_url
        self.info: WebhookInfo | None = None
        self._session: aiohttp.ClientSession | None = None

    async def _getses(self) -> aiohttp.ClientSession:
        """Helps with the ClientSession() to make a new session if closed or None"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Safely closes the session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def req_webhook(
            self,
            json_data: dict | None = None,
            type: str = 'get',
            data: dict | None = None,
            files: dict | None = None,
            msg_id: str | None = None
        ) -> aiohttp.ClientResponse:

        if getattr(self, 'info', None) is None and type != 'get':
            await self.fetch_metadata()
        
        session = await self._getses()

        if msg_id and type in ('patch', 'delete'):
            url = f'{self.webhook}/messages/{msg_id}'
        else:
            url = self.webhook

        if type in ('post'):
            url = f'{url}?wait=true'

        try:
            if type == 'get':
                response = await self._session.get(url)
                return await response.json()
            elif type == 'post':
                if files is not None:
                    response = await self._session.post(url, files=files)
                    return await response.json()
                else:
                    response = await self._session.post(url, json=json_data)
                    return await response.json()
            elif type == 'patch':
                if files is not None:
                    response = await self._session.patch(url, files=files)
                    return await response.json()
                else:
                    response = await self._session.patch(url, json=json_data)
                    return await response.json()
            elif type == 'delete':
                response = self._session.delete(url)
            else:
                raise ValueError('No type for that?')
        except aiohttp.ClientError as error:
            raise GeneralAPIError(f'Network error occured: {error}')

        if response.status == 400:
            try:
                jsonified = await response.json()
                disc_response = jsonified.get('message', 'Bad request error occured, maybe you answered a parameter wrong?')
            except (ValueError, aiohttp.ContentTypeError):
                disc_response = 'Invalid JSON response'
            raise BadRequest(disc_response)
        elif response.status == 429:
            raise RatelimitError("You've hit Discord's ratelimit, slow down!")
        
        try:
            response.raise_for_status()
            return response
        except aiohttp.ClientError as HTTPError:
            raise GeneralAPIError(f'HTTP Error occured: {HTTPError}')
        
    async def fetch_metadata(self):
        """Fetches the metadata of the webhook"""
        response = await self.req_webhook(type='get')

        self.info = WebhookInfo(response)

    async def send(self, message: Message, username: str | None = None, avatar_url: str | None = None):
        """Sends a message with the webhook"""
        if isinstance(message, str):
            payload = Message(content=message)

        payload = message.to_dict()

        if username is not None:
            payload['username'] = username
        if avatar_url is not None:
            payload['avatar_url'] = avatar_url

        if message.files:
            files_payload = message.get_files_payload()
            form_data = aiohttp.FormData()
            
            for key, (filename, fb, ct) in files_payload.items():
                form_data.add_field(
                    key,
                    fb,
                    filename=filename,
                    content_type=ct
                )

            try:
                response = await self.req_webhook(type='post', files=form_data)
                return await response.json()
            finally:
                for file_obj in message.files:
                    file_obj.close()
        else:
            response = await self.req_webhook(type='post', json_data=payload)
            return response
        
    async def edit(self, message_id: str, new_msg: Message | str):
        """Edits a message from the webhook"""
        if isinstance(new_msg, str):
            new_msg = Message(content=new_msg)

        payload = new_msg.to_dict()
        
        if new_msg.files:
            files_payload = new_msg.get_files_payload()
            form_data = {'payload_json': (None, json.dumps(payload), 'application/json')}
            form_data.update(files_payload)

            try:
                response = await self.req_webhook(type='patch', files=form_data, msg_id=message_id)
                return await response.json()
            finally:
                for file_obj in new_msg.files:
                    file_obj.close()
        else:
            response = await self.req_webhook(type='patch', json_data=payload, msg_id=message_id)
            return await response.json()
    
    async def delete(self, message_id: str):
        """Deletes a message from the webhook"""
        return await self.req_webhook(type='delete', msg_id=message_id)