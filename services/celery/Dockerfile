FROM django

RUN addgroup celery && adduser --system --disabled-login --no-create-home \
  --ingroup celery celery

RUN apt-get update && apt-get install -y inotify-tools

COPY ./celery/autoreload.sh /usr/local/bin/autoreload
RUN chmod a+x /usr/local/bin/autoreload
COPY ./django/manage.py /app/
COPY ./django/google_keyfile.json /app/

COPY ./django/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY ./django/backend/ /app/backend/
COPY ./django/cal/ /app/cal/
COPY ./django/chatbot/ /app/chatbot/
COPY ./django/roster/ /app/roster/

RUN chown -R celery:celery /app/

WORKDIR /app/
USER celery
