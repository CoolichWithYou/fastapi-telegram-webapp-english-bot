FROM python:3.13

RUN useradd --create-home --shell /bin/bash app

WORKDIR /server
COPY . /server
RUN pip install --no-cache-dir -r requirements.txt
COPY entrypoint.sh /entrypoint.sh

RUN chown -R app:app /server
USER app
RUN chmod +x entrypoint.sh

USER app

WORKDIR /
CMD ["/entrypoint.sh"]
