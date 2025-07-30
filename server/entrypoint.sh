#!/bin/sh


exec uvicorn server.main:app --host 0.0.0.0 --port $SERVER_PORT
