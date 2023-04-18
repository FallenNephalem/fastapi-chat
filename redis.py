from __future__ import annotations

import json
from enum import Enum
from typing import AsyncIterator, Optional

import aioredis as aioredis
from pydantic.main import BaseModel

redis_pool = None


async def configure_redis():
    global redis_pool
    if not redis_pool:
        pool = await aioredis.from_url('redis://redis:6379', decode_responses=True)
        redis_pool = pool


def get_redis() -> aioredis.Redis:
    return redis_pool


class EventType(str, Enum):
    participants = 'participants'
    message = 'message'
    history = 'history'


class Participants(BaseModel):
    event_type: EventType = EventType.participants
    participants: list[str]


class Message(BaseModel):
    event_type: EventType = EventType.message
    username: str
    message: str
    timestamp: str


class History(BaseModel):
    event_type: EventType = EventType.history
    messages: list[Message]

    @staticmethod
    def from_messages(messages: list[str]) -> History:
        messages = [Message(**json.loads(message)) for message in messages]
        messages.sort(key=lambda x: x.timestamp)
        return History(messages=messages)
