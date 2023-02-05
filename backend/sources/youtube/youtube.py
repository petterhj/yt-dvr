from pyyoutube import Api
from pyyoutube.error import PyYouTubeException

from config import (
    YT_API_KEY,
    YT_OUTPUT_TEMPLATE,
    YT_PLAYLIST_ID,
    YT_PLAYLIST_MAX_COUNT,
)
from exceptions import ItemNotFoundError
from models import Item, Job
from .models import YoutubeItem
from .tasks import YoutubeDownloadTask


api = Api(api_key=YT_API_KEY)


def get_config():
    return {
        "playlist_id": YT_PLAYLIST_ID,
        "output_template": YT_OUTPUT_TEMPLATE,
    }


def get_item(
    item_id: str,
) -> Item:
    video = api.get_video_by_id(video_id=item_id)

    if len(video.items) == 0:
        raise ItemNotFoundError

    video = YoutubeItem(item_id=item_id, **video.items[0].snippet.to_dict())
    return Item.parse_obj(video)


def get_playlist() -> list[Item]:
    try:
        playlist_items = api.get_playlist_items(
            playlist_id=YT_PLAYLIST_ID,
            count=YT_PLAYLIST_MAX_COUNT,
        ).items
    except PyYouTubeException as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.message,
        )

    items = []

    for item in playlist_items:
        video = item.snippet.to_dict()
        video_id = video["resourceId"]["videoId"]

        if video_id in [item.item_id for item in items]:
            # Skip any duplicates
            continue

        items.append(Item.parse_obj(YoutubeItem(**video)))

    return items


def get_download_task(session, job: Job) -> YoutubeDownloadTask:
    return YoutubeDownloadTask(session, job)
