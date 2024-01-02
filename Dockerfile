FROM python:3.8.18-bookworm

WORKDIR /app

# Install cmake
RUN apt-get update && apt-get install -y cmake

# Install witness encryption package
RUN git clone https://github.com/kofi-dalvik/bls-witness-encryption.git
RUN cd bls-witness-encryption && python setup.py install

# Install dependencies
RUN pip install blspy clickhouse-connect dotenv Flask gunicorn networkx numpy oblivious pybind11 pygroupsig redis requests rq