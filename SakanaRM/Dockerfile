FROM python:3.9-slim

WORKDIR /usr/src/SakanaRM

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Only in dev enviornment!
ENV DJANGO_SETTINGS_MODULE=SakanaRM.settings_dev

# Add following lines to avoid errors during "pip install mysqlclient"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       default-libmysqlclient-dev \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh .
# Remove carriage return
RUN sed -i 's/\r$//g' /usr/src/SakanaRM/entrypoint.sh
RUN chmod +x /usr/src/SakanaRM/entrypoint.sh

COPY . .

ENTRYPOINT ["/usr/src/SakanaRM/entrypoint.sh"]
