FROM django

RUN addgroup django && adduser --system --disabled-login --no-create-home \
  --ingroup django django

RUN apt-get update && apt-get install -y inotify-tools

COPY autoreload.sh /usr/local/bin/autoreload
RUN chmod a+x /usr/local/bin/autoreload

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY cal/ /app/cal/
COPY chatbot/ /app/chatbot/
COPY roster/ /app/roster/
COPY manage.py /app/
COPY google_keyfile.json /app/
COPY backend/ /app/backend/
COPY staticfiles/ /app/staticfiles/

EXPOSE 8000

USER django
