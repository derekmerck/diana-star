# Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'services.yml' are present in /usr/src/app (copy, mount, etc)
# - Change the queue by overriding CMD on start up

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
RUN sed -i 's^open(".*",^open("services.yml",^' diana-star/apps/celery/celerycfg.py
RUN echo "export PYTHONPATH=~/diana-star" >> .bashrc
RUN pip install -r diana-star/requirements.txt
RUN chown -R celery /home/celery/diana-star

USER celery
WORKDIR /home/celery/diana-star/apps/celery
CMD python dcelery.py worker