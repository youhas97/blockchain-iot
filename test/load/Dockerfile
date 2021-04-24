FROM ubuntu:bionic-20190204

RUN apt-get update && apt-get install -y python3.6 curl ash

RUN apt-get update && apt-get install -y python3-distutils

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

COPY requirements.txt /

RUN python3 -m pip install -r requirements.txt

EXPOSE 8089 5557 5558

ENTRYPOINT ["usr/local/bin/bash"]