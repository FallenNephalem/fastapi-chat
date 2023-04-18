import datetime
import json
from collections import defaultdict
from operator import itemgetter

from fastapi import WebSocket
from redis import get_redis, Message, Participants, History


class ChatManager:
    def __init__(self):
        self.channels = defaultdict(list)

    async def connect(self, ws: WebSocket, channel: str, username: str):
        if username not in map(itemgetter(0), self.channels[channel]):
            await ws.accept()
            self.channels[channel].append((username, ws))
            await self.send_history(ws, channel)
            for _, connection in self.channels[channel]:
                await self.update_users(connection, channel)
        # TODO: else send username error

    async def disconnect(self, ws, channel, username):
        self.channels[channel].remove((username, ws))
        for _, connection in self.channels[channel]:
            await self.update_users(connection, channel)

    async def receive_message(self, ws: WebSocket, channel):
        message = Message(**await ws.receive_json())
        await self._save(message, channel)
        await self.broadcast_message(message, channel)

    @staticmethod
    async def _save(message: Message, channel: str):
        await get_redis().lpush(channel, message.json().encode('utf-8'))
        await get_redis().ltrim(channel, 0, 10)

    async def broadcast_message(self, message: Message, channel: str):
        for username, connection in self.channels[channel]:
            if username != message.username:
                await connection.send_json(message.dict())

    async def update_users(self, ws: WebSocket, channel: str):
        participants = Participants(participants=list(map(itemgetter(0), self.channels[channel])))
        await ws.send_json(participants.dict())

    @staticmethod
    async def send_history(ws: WebSocket, channel: str):
        history = History.from_messages(await get_redis().lrange(channel, 0, 10))
        await ws.send_json(history.dict())
