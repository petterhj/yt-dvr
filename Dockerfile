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

RUN set -eux; \
	apt-get update; \
	apt-get install -y gosu python3 python3-pip ffmpeg cron curl; \
	rm -rf /var/lib/apt/lists/*; \
    # verify that the binary works
	gosu nobody true

RUN useradd -u $PUID -U -d /src -s /bin/false ytdvr && \
    usermod -G users ytdvr

RUN mkdir -p /app/save
RUN mkdir -p /app/data
RUN chown -R ytdvr /app

ADD ./app /app
ADD requirements.txt /app
ADD entry-point.sh /app

WORKDIR /app

RUN python3 -m pip install \
        --no-cache-dir \
        -r requirements.txt

ENTRYPOINT ["/app/entry-point.sh"]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
