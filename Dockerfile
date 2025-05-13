# Source: https://github.com/docker/awesome-compose/tree/master/flask
FROM python:3.12.1-alpine3.19 AS builder

WORKDIR /app

RUN apk add --no-cache git

# COPY requirements.txt /app
# RUN pip3 install -r requirements.txt

RUN pip install --upgrade pip && \
    pip install pandas numpy plotly krippendorff seaborn jinja2 scipy statsmodels

COPY . /app

# add a non-root user
RUN adduser -D -h /home/appuser -s /bin/sh appuser
USER appuser


#ENTRYPOINT ["python3"]
#RUN python3 CreateDatabase.py
CMD ["python3", "main.py"]
