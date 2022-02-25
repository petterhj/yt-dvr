# yt-dvr

## Local

```sh
# .env
OUTPUT_PATH=../
DATA_PATH=../
YT_API_KEY=<api_key>
YT_PLAYLIST_ID=<playlist_id>
YT_PLAYLIST_MAX_COUNT=5
YT_OUTPUT_TEMPLATE=%(channel)s - %(title)s.%(ext)s
```
```sh
cd app/
uvicorn main:app --reload
```

## Docker

```sh
docker build --tag ytdvr:latest .
docker run \
    -e YT_API_KEY=<api_key> \
    -e YT_PLAYLIST_ID=<playlist_id> \
    -e CRON_SCHEDULE="* */12 * * *"
    -v $(pwd)/save:/app/save
    -v $(pwd)/data:/app/data
    -p 8080:8000
    --name ytdvr
    ytdvr
```