# Minimal Diana Worker Image
# Derek Merck, Spring 2018
#
# - Presumes 'secrets.yml' are present in /usr/src/app (copy, mount, etc)
# - Change the queue by overriding CMD on start up

FROM python:3.6-stretch

MAINTAINER Derek Merck <derek_merck@brown.edu>

RUN apt install -y git

WORKDIR /usr/src/app

RUN pip install git+https://github.com/derekmerck/diana-star

RUN sed -i "s^open\(\"(.*)\",^services.yml^" /usr/src/app/diana-star/apps/celery/celerycfg.py

CMD python /usr/src/app/diana-star/apps/celery/dcelery.py worker