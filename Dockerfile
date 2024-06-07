FROM python:3.11

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./index.py .

EXPOSE 8000

CMD ["python", "index.py"]
