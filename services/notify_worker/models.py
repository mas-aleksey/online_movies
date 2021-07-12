from datetime import datetime
from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel


class Channel(str, Enum):
    email = 'email'
    sms = 'sms'
    web = 'web'


class NotifyType(str, Enum):
    immediately = 'immediately'
    scheduled = 'scheduled'


class Notification(str, Enum):
    hello_message = 'hello_message'
    new_movies = 'new_movies'
    scheduled_message = 'scheduled_message'


class User(BaseModel):
    user_id: str
    username: str
    email: str
    timezone: str
    allowed_channels: Dict[Notification, List[Channel]]

    def has_allowed_channel(self, notice: Notification, channel: Channel):
        """разрешено ли уведомление в канал."""
        return channel in self.allowed_channels.get(notice, [])


class EventMessage(BaseModel):
    name: Notification
    type: NotifyType
    payload: Dict[str, Any]
    channels: List[Channel]
    users: List[User]
    timestamp: datetime


class TemplateMessage(BaseModel):
    short_text: str
    message: str
