# Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'services.yml' are present in /usr/src/app (copy, mount, etc)
# - Change the queue by overriding CMD on start up

FROM python:3.6-stretch

MAINTAINER Derek Merck <derek_merck@brown.edu>

WORKDIR /usr/src/app

RUN apt update && apt install -y git

RUN git clone https://github.com/derekmerck/diana-star

RUN pip install -r diana-star/requirements.txt

RUN sed -i 's^open("(.*)",^services.yml^' /usr/src/app/diana-star/apps/celery/celerycfg.py

ENV PYTHONPATH="/usr/src/app/diana-star"

CMD python /usr/src/app/diana-star/apps/celery/dcelery.py worker