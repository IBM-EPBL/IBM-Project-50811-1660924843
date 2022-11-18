FROM python:3.6.5-alpine
WORKDIR /flask
ADD . /flask

RUN set -e; \
        apk add --no-cache --virtual .build-deps \
                gcc \
                libc-dev \
                linux-headers \
                mariadb-dev \
                python3-dev \
                postgresql-dev \
        ;
COPY requirements.txt /flask
RUN pip install -r requirements.txt
CMD ["python","index.py"]