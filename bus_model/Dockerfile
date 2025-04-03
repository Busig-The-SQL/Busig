
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y libpq-dev build-essential

WORKDIR /bus_model

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=/bus_model/app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5002

# cronjob minutely running update_GTFS_Realtime.sh
RUN chmod +x /bus_model/scripts/update_GTFS_Realtime.sh

RUN echo "* * * * * root /bus_model/scripts/update_GTFS_Realtime.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/bus_update
RUN chmod 0644 /etc/cron.d/bus_update

# Register the cron job
RUN crontab /etc/cron.d/bus_update

RUN pip install gunicorn
CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5002", "app:app"]
