from typing import Dict, Optional

from a2wsgi import ASGIMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

from telegram import telegram_hook_search_note


app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


class TelegramHookItem(BaseModel):
    message: Optional[Dict]
    callback_query: Optional[Dict]


@app.post('/api/v1/note/hook/telegram/{token}/')
async def _telegram_hook_search_note(token: str, hook_item: TelegramHookItem):
    return telegram_hook_search_note(hook_item.dict(), token)


# mod_wsgi expects the name 'application' by default
application = ASGIMiddleware(app)