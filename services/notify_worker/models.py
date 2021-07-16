from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel

from utils.users import get_allow_channels_from_db, get_user_info_from_auth


class Channel(str, Enum):
    email = 'email'
    sms = 'sms'
    web = 'web'


class NotifyType(str, Enum):
    immediately = 'immediately'
    scheduled = 'scheduled'


class User(BaseModel):
    user_id: str
    username: Optional[str]
    email: Optional[str]
    timezone: Optional[str]
    allowed_channels: Optional[Dict[str, List[Channel]]]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        if not self.allowed_channels:
            self.allowed_channels = get_allow_channels_from_db(self.user_id)

        user_info = get_user_info_from_auth(self.user_id)
        if not self.username:
            self.username = user_info['username']
        if not self.email:
            self.email = user_info['email']

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
