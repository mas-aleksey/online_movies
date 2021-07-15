from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel
import core.settings as settings


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


class EventMessage(BaseModel):
    name: str
    type: NotifyType
    payload: Dict[str, Any]
    channels: List[Channel]
    users: List[User]
    timestamp: str = datetime.utcnow().strftime(settings.DEFAULT_DATE_FORMAT)
