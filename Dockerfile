FROM python:3.10

WORKDIR /app

RUN pip install requests beautifulsoup4

COPY . .

CMD ["python", "script.py"]
