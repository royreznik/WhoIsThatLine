FROM python:3.12-slim

RUN pip install uv

WORKDIR /app/

COPY uv.lock pyproject.toml .

RUN uv sync --frozen

COPY whoisthatline/ whoisthatline/ 

CMD [ "uv", "run", "uvicorn", "--host", "0.0.0.0", "whoisthatline.web_app:app" ]
