FROM python:3.6 as base

# Bug in pipenv, where it does not find python in the PATH 
RUN ln -sf $(which python) /bin/python

WORKDIR /usr/src/app
COPY Pipfile* ./
RUN pip install pipenv==9.0.1
RUN pipenv install --system

from base as production
COPY writer writer/
COPY run.sh ./
CMD ["bash", "run.sh"]

FROM production as development
RUN pipenv install --system --dev
CMD ["bash", "run.sh"]
