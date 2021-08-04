FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1

RUN addgroup --gid 3000 xently && \
    adduser --disabled-password --uid 3000 xently --ingroup xently

WORKDIR /app/

COPY --chown=3000:3000 . ./

RUN apk -U upgrade && \
    apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev cargo && \
    pip install -U pip wheel && \
    pip install --use-feature=in-tree-build --no-cache-dir -Ur requirements.txt && \
    rm -Rf build && \
	rm -Rf django_rest_xauth.egg-info && \
    apk del gcc musl-dev python3-dev libffi-dev openssl-dev cargo

# Need to create an sqlite database file. Therefore, to avoid permission errors we'll run as root
#USER 3000:3000

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
