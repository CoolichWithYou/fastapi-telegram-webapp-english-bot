FROM python:3.13
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /

CMD ["/entrypoint.sh"]
