# Usage:
#
# /strictdoc$ docker build . -t strictdoc:0.0.18
# /strictdoc$ docker run --name strictdoc --rm -v "$(pwd)/docs:/data" -i -t strictdoc:0.0.18
# bash-5.1# strictdoc export .
# bash-5.1# exit
# strictdoc$ firefox docs/output/html/index.html

FROM python:3.10-alpine

RUN apk add --no-cache bash

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir strictdoc==0.0.18

WORKDIR /data

ENTRYPOINT /bin/bash
