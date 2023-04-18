from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from chat import ChatManager
from redis import configure_redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    await configure_redis()
    yield


app = FastAPI(lifespan=lifespan)
router = APIRouter(
    prefix='/api',
)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
manager = ChatManager()


@app.get('/', response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})


@app.websocket("/ws/chat/{channel}/{username}")
async def chat(websocket: WebSocket, channel: str, username: str):
    await manager.connect(websocket, channel, username)
    try:
        while True:
            await manager.receive_message(websocket, channel)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel, username)


@app.get('/', response_class=HTMLResponse)
async def last_messages(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})


@router.get('/health', response_class=JSONResponse)
async def health_check():
    return {'status': 'ok'}

app.include_router(router)
