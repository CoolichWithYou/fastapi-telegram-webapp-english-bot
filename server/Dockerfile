FROM python:3.13
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R app:app /server

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

USER app

WORKDIR /

CMD ["/entrypoint.sh"]
