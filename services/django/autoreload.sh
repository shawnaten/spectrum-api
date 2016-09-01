#!/bin/sh

FILES="$(find . -name "*.py")"

while true; do
  gunicorn -b 0.0.0.0 backend.wsgi &
  PID=$!
  echo $PID
  inotifywait -e modify ${FILES}
  kill $PID
done
