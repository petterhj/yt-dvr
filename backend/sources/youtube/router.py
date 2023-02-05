from typing import List

from fastapi import APIRouter, Depends

from .youtube import get_playlist
from models import ItemOut


router = APIRouter(prefix="/youtube")

@router.get(
    "/playlist",
    response_model=List[ItemOut],
    response_model_by_alias=False,
)
async def playlist(
    items = Depends(get_playlist)
):
    return [item.dict() for item in items]
