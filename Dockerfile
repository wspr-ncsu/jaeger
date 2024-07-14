FROM python:3.8-slim

WORKDIR /app

# Install cmake
RUN apt-get update && apt-get install -y cmake git libsodium23 libsodium-dev build-essential 

COPY requirements.txt .
COPY install-witenc.sh .

RUN pip install -r requirements.txt
RUN ./install-witenc.sh

COPY . .

