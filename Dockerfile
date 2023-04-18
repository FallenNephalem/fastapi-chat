FROM python:3.10

WORKDIR /usr/src/app

ENV APP_PORT 8080
ENV APP_NUM_WORKERS 2
ENV PYTHONPATH /usr/src/app
ENV PYTHONUNBUFFERED TRUE
ENV PYTHONHTTPSVERIFY 0

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

CMD exec uvicorn --workers $APP_NUM_WORKERS --host 0.0.0.0 --port $APP_PORT app:app --reload
