#!/bin/sh

FILES="$(find . -name "*.py")"

while true; do
  celery -A backend worker -l info &
  PID=$!
  echo $PID
  inotifywait -e modify ${FILES}
  kill $PID
done
