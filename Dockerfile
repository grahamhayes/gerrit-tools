FROM ubuntu:16.04

MAINTAINER Graham Hayes version: 0.0.1

RUN apt-get update && apt-get install -y python python-launchpadlib python-jinja2 python-requests && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY lp/lp-dash.py lp/lp-dash.py

CMD python lp/lp-dash.py -p designate