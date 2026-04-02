import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from web.schemas import Question, Answer
from web.service import ChatService

from configuration.config import *

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(WEB_STATIC_DIR)), name="static")
service = ChatService()

@app.get("/")
def read_root():
    return RedirectResponse("/static/index.html")

@app.post("/api/chat")
def read_item(question: Question) -> Answer:
    answer = service.chat(question.message)
    return Answer(message=answer)

if __name__ == '__main__':
    uvicorn.run('web.app:app', host='0.0.0.0', port=8000)
