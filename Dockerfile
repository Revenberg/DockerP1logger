FROM python:alpine3.7

RUN pip install --upgrade pip && pip uninstall serial

COPY files/requirements.txt /app/
RUN pip install -r requirements.txt

COPY files/app* /app/
COPY config/* /app/
WORKDIR /app

CMD python ./p1logger.py
