from __future__ import annotations

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
    
class Message:
    """A message object that can be sent in webhooks"""
    def __init__(self, content: str, embeds: list[Embed] | None = None):
        self.content = content
        self.embeds = embeds

    def to_dict(self) -> dict:
        """Returns a dictionary version of the object"""
        dictionary = {'content': self.content}
        if self.embeds is not None:
            dictionary['embeds'] = [embed.to_dict() for embed in self.embeds]
        return dictionary