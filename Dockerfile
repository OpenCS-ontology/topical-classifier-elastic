FROM python:3.10.9-slim-bullseye

WORKDIR /home
RUN mkdir output
RUN mkdir source
COPY source source
COPY config.py config.py
COPY pipeline.py pipeline.py
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install -y git
RUN pip3 install -r /home/requirements.txt
RUN git clone https://github.com/OpenCS-ontology/OpenCS