from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from models import Item


async def get_items(
    source: str = None,
    session: Session = Depends(get_session),
) -> list[Item]:
    if source:
        items = await session.query(Item, Item.source == source)
    else:
        items = await session.query(Item)
    return items


async def get_item(
    source: str,
    item_id: str,
    session: Session = Depends(get_session),
) -> Item:
    print("?"*100)
    item = await session.first_or_none(
        Item,
        Item.source == source,
        Item.item_id == item_id,
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No item found for {source}:{item_id}",
        )
    
    return item

