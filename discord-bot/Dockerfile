FROM python:3.12-slim

WORKDIR /app

COPY discord-bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY discord-bot/ .
COPY shared/ /shared/

CMD ["python", "bot.py"]
