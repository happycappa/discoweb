from __future__ import annotations

from pathlib import Path


class Embed:
    """A simple Discord embed object"""
    def __init__(self, title: str | None = None, description: str | None = None, color: str = '#FFFFFF'):
        self.title = title
        self.description = description
        self.color = color

    def convert_hex(self) -> int:
        """Converts the hexcode color to integers for the Discord API"""
        hexstr = self.color.lstrip("#")
        try:
            return int(hexstr, 16)
        except ValueError:
            return 0

    def to_dict(self) -> dict:
        """Returns a dictionary version of the object"""
        dictionary = {}
        if self.title: dictionary['title'] = self.title
        if self.description: dictionary['description'] = self.description
        if self.color: dictionary['color'] = self.color

class EmbedPlus(Embed):
    """A embed object with more options"""
    def __init__(self, title: str | None = None, description: str | None = None, color: str = '#FFFFFF', image_url: str | None = None,
                 thumbnail_url: str | None = None):
        self.title = title
        self.description = description
        self.color = color
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url

        self._author = {}
        self._footer = {}
        self._fields = []

    def convert_hex(self) -> int:
        """Converts the hexcode color to integers for the Discord API"""
        hexstr = self.color.lstrip('#')
        try:
            return int(hexstr, 16)
        except ValueError:
            return 0

    def set_author(self, author: str, icon_url: str | None = None, url: str | None = None):
        """Sets the author on your embed"""
        if len(author) > 256:
            raise ValueError('Embed author name cannot exceed 256 characters.')

        self._author = {
            'name': author,
            'url': url,
            'icon_url': icon_url
        }
        return self

    def set_footer(self, text: str, icon_url: str | None = None):
        """Sets the footer on your embed"""
        if len(text) > 2048:
            raise ValueError('Embed author name cannot exceed 256 characters.')

        self._footer = {
            'text': text,
            'icon_url': icon_url
        }
        return self

    def add_field(self, name: str, value: str, inline: bool = True):
        """Adds a field to the embed"""
        if len(name) > 256:
            raise ValueError('Field name cannot exceed 256 characters.')
        if len(value) > 1024:
            raise ValueError('Field value cannot exceed 1024 characters.')
        if len(self._fields) >= 25:
            raise ValueError('You have too much fields, the max is 25!')

        self._fields.append({
            'name': name,
            'value': value,
            'inline': inline
        })
        return self

    def to_dict(self) -> dict:
        """Returns a dictionary version of the object"""
        dictionary = {}
        if self.title: dictionary['title'] = self.title
        if self.description: dictionary['description'] = self.description
        if self.color: dictionary['color'] = self.convert_hex()
        if self.thumbnail_url: dictionary['thumbnail'] = {'url': self.thumbnail_url}
        if self.image_url: dictionary['image'] = {'url': self.image_url}

        if self._author: dictionary['author'] = {k: v for k, v in self._author.items() if v is not None}
        if self._footer: dictionary['footer'] = {k: v for k, v in self._author.items() if v is not None}
        if self._fields: dictionary['fields'] = self._fields
        return {k: v for k, v in dictionary.items() if v not in (None, {}, [])}

class File:
    """A file object that contains media inside it"""
    def __init__(self, file_path: str | Path, filename: str | None = None):
        self.fp = Path(file_path) if isinstance(file_path, str) else file_path
        if not self.fp.is_file():
            raise FileNotFoundError(f'Could not find the file associated with the path: {self.fp}')
        self.filename = filename or self.fp.name
        self._file_stream = None

    def read_bytes(self):
        """Reads the file's bytes"""
        return self.fp.read_bytes()

    def open(self):
        """Opens the file object in binary read mode and creates a stream"""
        self._file_stream = open(self.fp, "rb")
        return (self.filename, self._file_stream)

    def close(self):
        """Safely closes the file to prevent system memory leaks"""
        if self._file_stream and not self._file_stream.closed:
            self._file_stream.close()

class AllowedMentions:
    """Object to manage who can be mentioned"""
    def __init__(
        self,
        everyone: bool = True,
        users: bool | list[str] = True,
        roles: bool | list[str] = True,
        replied_user: bool | list[str] = True
    ):
        self.everyone = everyone
        self.users = users
        self.roles = roles
        self.replied = replied_user

    def to_dict(self) -> dict:
        """Returns a dictionary version of the object"""
        parsed = []
        dictionary = {}

        if self.everyone: parsed.append('everyone')

        if self.users is True:
            parsed.append(self.users)
        elif isinstance(self.users, list):
            parsed.append('users')
            dictionary['users'] = [str(u_id) for u_id in self.users]
        else:
            dictionary['users'] = []

        if self.roles is True:
            parsed.append(self.roles)
        elif isinstance(self.roles, list):
            parsed.append('roles')
            dictionary['roles'] = [str(r_id) for r_id in self.roles]
        else:
            dictionary['roles'] = []

        dictionary['parse'] = parsed
        dictionary['replied_user'] = self.replied
        return dictionary

class Message:
    """A message object that can be sent in webhooks"""
    def __init__(
            self, content: str | None = None, files: list[File] | None = None, embeds: list[Embed | EmbedPlus] | None = None,
            allowed_mentions: AllowedMentions | None = None):
        self.content = content
        self.embeds = embeds or []
        self.files = files or []
        self.all_m = allowed_mentions

    def to_dict(self) -> dict:
        """Returns a dictionary version of the object"""
        dictionary = {}
        if self.embeds is not None:
            dictionary['embeds'] = [embed.to_dict() for embed in self.embeds]
        if self.content is not None:
            dictionary['content'] = self.content
        if self.all_m is not None:
            dictionary['allowed_mentions'] = self.all_m.to_dict()
        return dictionary

    def get_files_payload(self) -> dict:
        """Opens and groups the files into a form-data dictionary structure"""
        payload = {}
        for index, file_obj in enumerate(self.files):
            fbytes = file_obj.read_bytes()

            payload[f'files[{index}]'] = (
                file_obj.filename,
                fbytes,
                'application/octet-stream'
            )
        return payload
