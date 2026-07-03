from __future__ import annotations
import os

class Embed:
    """A simple Discord embed object"""
    def __init__(self, title: str, description: str, color: str = '#FFFFFF'):
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
        return {
            "title": self.title,
            "description": self.description,
            "color": self.convert_hex()
        }
    
class File:
    """A file object that contains media inside it"""
    def __init__(self, file_path: str, filename: str | None = None):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find the file associated with the path: {file_path}")
        self.fp = file_path
        self.filename = filename
        self._file_stream = None

    def open(self):
        """Opens the file object in binary read mode and creates a stream"""
        self._file_stream = open(self.fp, "rb")
        return (self.filename, self._file_stream)
    
    def close(self):
        """Safely closes the file to prevent system memory leaks"""
        if self._file_stream and not self._file_stream.closed:
            self._file_stream.close()
    
class Message:
    """A message object that can be sent in webhooks"""
    def __init__(self, content: str, files: list[File] | None = None, embeds: list[Embed] | None = None):
        self.content = content
        self.embeds = embeds or []
        self.files = files or []

    def to_dict(self) -> dict:
        """Returns a dictionary version of the object"""
        dictionary = {'content': self.content}
        if self.embeds is not None:
            dictionary['embeds'] = [embed.to_dict() for embed in self.embeds]
        return dictionary
    
    def get_files_payload(self) -> dict:
        """Opens and groups the files into a form-data dictionary structure"""
        payload = {}
        for index, file_obj in enumerate(self.files):
            payload[f'files[{index}]'] = file_obj.open()
        return payload