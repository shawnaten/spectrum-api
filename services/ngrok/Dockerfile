FROM ubuntu

RUN addgroup ngrok && adduser --system --disabled-login --no-create-home \
  --ingroup ngrok ngrok

RUN apt-get update && apt-get install -y unzip

COPY ngrok.yml /opt/ngrok/conf/ngrok.yml

ADD https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip ngrok-stable-linux-amd64.zip

RUN unzip ngrok-stable-linux-amd64.zip && chmod a+x ngrok && \
  mv ngrok /usr/local/bin/ngrok && rm ngrok-stable-linux-amd64.zip

USER ngrok

CMD ngrok start -authtoken=${NGROK_AUTH_TOKEN} \
  -config=/opt/ngrok/conf/ngrok.yml --all
