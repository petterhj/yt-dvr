#!/bin/bash

echo "Configuring cron job: ${CRON_SCHEDULE}"

echo "${CRON_SCHEDULE} curl \
    --silent http://localhost:8000/videos/process \
    >/dev/null 2>&1" >> ytdvr_cronjob

crontab ytdvr_cronjob
rm ytdvr_cronjob
/etc/init.d/cron restart

echo "Starting app with uid=${PUID}, gid=${PGID}"

groupmod -o -g "$PGID" ytdvr
usermod -o -u "$PUID" ytdvr

exec /usr/sbin/gosu ytdvr:ytdvr "$@"
