FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE.txt ./
COPY shpr ./shpr

RUN pip install --upgrade pip && \
    pip install --no-cache-dir "flit_core<4" && \
    pip install --no-cache-dir .

EXPOSE 7477

ENV FLASK_APP=shpr
ENV FLASK_RUN_PORT=7477
ENV FLASK_RUN_HOST=0.0.0.0

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
