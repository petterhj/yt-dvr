FROM node:16-alpine AS build_frontend

COPY ./frontend /src

WORKDIR /src

RUN npm ci --production
RUN npm run generate


FROM debian:sid-slim

ENV PUID=1000
ENV PGID=100
ENV OUTPUT_PATH=/app/save
ENV DATA_PATH=/app/data
ENV CRON_SCHEDULE="0 */12 * * *"
ENV YT_API_KEY=
ENV YT_PLAYLIST_ID=
ENV YT_PLAYLIST_MAX_COUNT=10
ENV YT_OUTPUT_TEMPLATE="%(channel)s - %(title)s.%(ext)s"
ENV STATIC_FILES_PATH=/app/static

RUN set -eux; \
	apt-get update; \
	apt-get install -y gosu python3 python3-pip ffmpeg cron curl; \
	rm -rf /var/lib/apt/lists/*; \
	gosu nobody true

RUN mkdir -p /app/static && mkdir /app/save && mkdir /app/data

RUN useradd -u $PUID -U -d /app -s /bin/false ytdvr && \
    usermod -G users ytdvr && \
    chown -R ytdvr /app

ADD ./backend /app
COPY --from=build_frontend /src/dist /app/static

COPY ./entry-point.sh /app/entry-point.sh
RUN chmod +x /app/entry-point.sh

WORKDIR /app

RUN python3 -m pip install \
        --no-cache-dir \
        -r requirements.txt

ENTRYPOINT ["/app/entry-point.sh"]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
