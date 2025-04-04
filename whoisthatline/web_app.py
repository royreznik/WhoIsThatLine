import pathlib
import random
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .game_logic import (
    select_code_snippet,
    select_other_members,
)

app = FastAPI()
templates = Jinja2Templates(directory=pathlib.Path(__file__).parent / "templates")


class Answer(BaseModel):
    author: str


class Feedback(BaseModel):
    correct: bool
    score: int


score: int = 0
current_snippet: list[str] | None = None
current_author: str | None = None
current_options: list[str] = []


@app.get("/")
def read_root(request: Request) -> Any:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/start")
def start_game(repo_path: str) -> dict[str, list[str]]:
    global current_snippet, current_author, current_options

    current_snippet, current_author = select_code_snippet(repo_path)
    if not current_snippet or not current_author:
        raise HTTPException(status_code=404, detail="No suitable code snippet found")

    current_options = select_other_members(repo_path, current_author)
    current_options.append(current_author)
    random.shuffle(current_options)

    return {"code_snippet": current_snippet, "options": current_options}


@app.post("/answer")
def submit_answer(answer: Answer) -> Feedback:
    global score
    if current_author is None:
        raise HTTPException(status_code=400, detail="Game not started yet")

    if answer.author == current_author:
        score += 1
        return Feedback(correct=True, score=score)
    else:
        return Feedback(correct=False, score=score)


@app.get("/score")
def get_score() -> dict[str, int]:
    return {"score": score}
