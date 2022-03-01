import os


DATA_PATH = os.path.abspath(os.environ["DATA_PATH"])
OUTPUT_PATH = os.path.abspath(os.environ["OUTPUT_PATH"])
DB_FILE_PATH = os.path.join(DATA_PATH, "log.db")
LOG_FILE_PATH = os.path.join(DATA_PATH, "ytdvr.log")
CRON_SCHEDULE = os.getenv("CRON_SCHEDULE")
YT_API_KEY = os.environ["YT_API_KEY"]
YT_PLAYLIST_ID = os.environ["YT_PLAYLIST_ID"]
YT_PLAYLIST_MAX_COUNT = int(os.getenv("YT_PLAYLIST_MAX_COUNT", 3))
YT_OUTPUT_TEMPLATE = os.getenv(
    "YT_OUTPUT_TEMPLATE",
    "%(title)s [%(id)s].%(ext)s",
)
YT_DLP_REFERER = "https://www.google.com"
