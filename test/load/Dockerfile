FROM ubuntu:bionic-20190204

RUN apt update && apt install -y python3 ash python-all-dev libevent-dev

RUN apt update && apt install -y python3-pip python3-distutils python3-greenlet

COPY requirements.txt /

RUN python3 -m pip install -r requirements.txt

EXPOSE 8089 5557 5558

ENTRYPOINT ["usr/local/bin/bash"]
