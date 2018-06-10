# Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'diana_services.yml' is copied or mounted to /etc/diana_services.yml
# - Change the queue by overriding CMD on start up
#   e.g., command="python dcelery.py worker -B -Q my_queue"

FROM python:3.6-stretch
MAINTAINER Derek Merck <derek_merck@brown.edu>

RUN apt update  \
  && apt install -y git

ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

RUN useradd -ms /bin/bash celery
WORKDIR /home/celery
RUN git clone https://github.com/derekmerck/diana-star

WORKDIR /home/celery/diana-star
RUN pip install -e packages/diana packages/guid-mint
RUN sed -i 's^open(".*",^open("/etc/diana_services.yml",^' apps/celery/celerycfg.py
RUN chown -R celery /home/celery/diana-star

USER celery
WORKDIR /home/celery/diana-star/apps/celery
CMD python dcelery.py worker