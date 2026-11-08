FROM python:3.11-slim

WORKDIR /app

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

CMD ["python", "kitesurf_bot.py", "--poll"]
