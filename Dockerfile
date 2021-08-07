FROM python:alpine3.7

RUN pip install --upgrade pip && pip uninstall serial

COPY files/* /app/
COPY config/* /app/
WORKDIR /app
RUN pip install -r requirements.txt

CMD python ./p1logger.py
