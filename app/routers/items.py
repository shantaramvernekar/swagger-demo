from typing import Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Path, Query, status

from app.schemas.item import Item, ItemCreate


router = APIRouter(prefix="/items", tags=["items"])


DB: Dict[int, Item] = {}


@router.post(
    "",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    summary="Create item",
    responses={201: {"description": "Item created"}, 422: {"description": "Validation error"}},
)
def create_item(
    payload: ItemCreate = Body(
        ...,
        examples={
            "basic": {"summary": "Basic", "value": {"name": "Widget", "price": 9.99}},
            "withTags": {
                "summary": "With tags",
                "value": {"name": "Gadget", "price": 19.5, "tags": ["new", "hot"]},
            },
        },
    )
):
    new_id = (max(DB.keys()) + 1) if DB else 1
    item = Item(id=new_id, **payload.model_dump())
    DB[new_id] = item
    return item


@router.get("", response_model=List[Item], summary="List items")
def list_items(
    q: Optional[str] = Query(default=None, description="Search by name substring"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items: List[Item] = list(DB.values())
    if q:
        items = [i for i in items if q.lower() in i.name.lower()]
    return items[offset : offset + limit]


@router.get("/{item_id}", response_model=Item, summary="Get item by id", responses={404: {"description": "Item not found"}})
def get_item(item_id: int = Path(..., ge=1, description="Item ID")):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Not found")
    return DB[item_id]


@router.put("/{item_id}", response_model=Item, summary="Replace item")
def replace_item(item_id: int = Path(..., ge=1), payload: ItemCreate = Body(...)):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Not found")
    item = Item(id=item_id, **payload.model_dump())
    DB[item_id] = item
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete item")
def delete_item(item_id: int = Path(..., ge=1)):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Not found")
    del DB[item_id]
    return

