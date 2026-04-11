FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir openenv-core fastapi "uvicorn[standard]" websockets pydantic openai httpx

COPY . .

ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]
