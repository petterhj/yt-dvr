#!/bin/bash

groupmod -o -g "$PGID" ytdvr
usermod -o -u "$PUID" ytdvr

echo "Starting with uid=${PUID}, gid=${PGID}"

exec /usr/sbin/gosu ytdvr:ytdvr "$@"
