from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel

from utils.users import get_allow_channels_from_db


class Channel(str, Enum):
    email = 'email'
    sms = 'sms'
    web = 'web'


class NotifyType(str, Enum):
    immediately = 'immediately'
    scheduled = 'scheduled'


class User(BaseModel):
    user_id: str
    username: str
    email: str
    timezone: str
    allowed_channels: Optional[Dict[str, List[Channel]]]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if not self.allowed_channels:
            self.allowed_channels = get_allow_channels_from_db(self.user_id)

    def has_allowed_channel(self, notice: str, channel: Channel):
        """разрешено ли уведомление в канал."""
        return channel in self.allowed_channels.get(notice, [])


class EventMessage(BaseModel):
    name: str
    type: NotifyType
    payload: Dict[str, Any]
    channels: List[Channel]
    users: List[User]
    timestamp: datetime


class TemplateMessage(BaseModel):
    short_text: str
    message: str
