# Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'services.yml' are present in /usr/src/app (copy, mount, etc)
# - Change the queue by overriding CMD on start up

FROM python:3.6-stretch
MAINTAINER Derek Merck <derek_merck@brown.edu>

RUN apt update  \
  && apt install -y git

RUN useradd -ms /bin/bash celery

USER celery
WORKDIR /home/celery

RUN git clone https://github.com/derekmerck/diana-star \
  && pip install -r diana-star/requirements.txt

RUN sed -i 's^open("(.*)",^services.yml^' diana-star/apps/celery/celerycfg.py
RUN echo "export PYTHONPATH=/usr/src/app/diana-star" >> .bashrc

CMD python diana-star/apps/celery/dcelery.py worker