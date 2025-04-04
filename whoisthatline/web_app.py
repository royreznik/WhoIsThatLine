from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from .game_logic import select_code_snippet, select_other_members, handle_multiline_comments, handle_multiple_authors
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Answer(BaseModel):
    author: str

class Feedback(BaseModel):
    correct: bool
    score: int

score = 0
current_snippet = None
current_author = None
current_options = []

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/start")
def start_game(repo_path: str):
    global current_snippet, current_author, current_options
    current_snippet, current_author = select_code_snippet(repo_path)
    if not current_snippet:
        raise HTTPException(status_code=404, detail="No suitable code snippet found")
    current_options = select_other_members(repo_path, current_author)
    current_options.append(current_author)
    random.shuffle(current_options)
    return {"code_snippet": current_snippet, "options": current_options}

@app.post("/answer")
def submit_answer(answer: Answer):
    global score
    if answer.author == current_author:
        score += 1
        return Feedback(correct=True, score=score)
    else:
        return Feedback(correct=False, score=score)

@app.get("/score")
def get_score():
    return {"score": score}

@app.get("/leaderboard")
def get_leaderboard():
    # Placeholder for leaderboard implementation
    return {"leaderboard": []}
