FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

COPY . ./

RUN apk -U upgrade && \
    apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev cargo && \
    pip install -U pip wheel && \
    pip install --no-cache-dir -Ur requirements.txt && \
    rm -Rf build && \
	rm -Rf django_rest_xauth.egg-info && \
    apk del gcc musl-dev python3-dev libffi-dev openssl-dev cargo

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
