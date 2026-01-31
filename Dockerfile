FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

CMD ["python", "run.py"]

# docker build -t my-bot
# docker run -d --env-file .env --name my_bot my-bot
