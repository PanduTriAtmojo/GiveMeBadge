FROM python:3-alpine

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY ./index.py .

CMD ["python", "index.py"]
