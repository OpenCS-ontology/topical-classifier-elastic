FROM python:3.10.9-slim-bullseye

WORKDIR /home
RUN mkdir output
RUN mkdir concepts_json
COPY pipeline.py pipeline.py
COPY requirements.txt requirements.txt
RUN pip3 install -r /home/requirements.txt