# Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'services.yml' is copied or mounted to /home/diana-star/apps/celery/
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

RUN git clone https://github.com/derekmerck/diana-star
RUN pip install -e /home/celery/diana-star/packages
RUN sed -i 's^open(".*",^open("services.yml",^' /home/celery/diana-star/apps/celery/celerycfg.py
#RUN echo "export PYTHONPATH=~/diana-star" >> .bashrc
#RUN pip install -r diana-star/requirements.txt
RUN chown -R celery /home/celery/diana-star

WORKDIR /home/celery
USER celery
WORKDIR /home/celery/diana-star/apps/celery
CMD python dcelery.py worker