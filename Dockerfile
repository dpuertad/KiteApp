FROM python:3.11-slim

WORKDIR /app

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

COPY . /app

CMD ["python", "kitesurf_bot.py", "--poll"]
