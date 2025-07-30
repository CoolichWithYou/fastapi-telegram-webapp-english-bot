#!/bin/bash

cleanup() {
  echo "Stopping all processes..."
  kill 0
  sudo docker compose down
}

trap cleanup SIGINT

sudo docker compose up --build -d db redis rabbitmq

export $(grep -v '^#' .env | xargs)

(cd server && uvicorn main:app --host 0.0.0.0 --port 8000) &
(cd bot && python main.py) &

wait