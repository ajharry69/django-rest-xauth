FROM python:3.9-alpine

ENV PYTHONUNBUFFERED=1

RUN groupadd --gid 3000 xently \
    && useradd --uid 3000 --gid 3000 xently

WORKDIR /app/

COPY --chown=3000:3000 . ./

RUN pip install --use-feature=in-tree-build -U . && \
    rm -R build || true && \
	rm -R django_rest_xauth.egg-info || true

USER 3000:3000

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint"]
