from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from api.schemas import (
    WatchListResponse,
    WatchListCreate,
    WatchListUpdate,
    WatchListItemCreate,
    WatchListItemInDB,
)
from api.dependencies import get_current_user
from apps.accounts.models import User, WatchList, WatchListItem
from apps.stocks.models import Stock

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.get("/", response_model=List[WatchListResponse])
async def list_watchlists(
    current_user: User = Depends(get_current_user),
):
    """
    현재 사용자의 관심목록 조회
    """
    watchlists = WatchList.objects.filter(user=current_user).prefetch_related(
        "items__stock"
    )

    result = []
    for watchlist in watchlists:
        wl_dict = WatchListResponse.model_validate(watchlist).model_dump()
        wl_dict["items"] = [
            {
                "id": item.id,
                "watchlist_id": item.watchlist_id,
                "stock_id": item.stock_id,
                "stock_code": item.stock.code,
                "stock_name": item.stock.name,
            }
            for item in watchlist.items.all()
        ]
        result.append(WatchListResponse(**wl_dict))

    return result


@router.post("/", response_model=WatchListResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    watchlist_in: WatchListCreate,
    current_user: User = Depends(get_current_user),
):
    """
    관심목록 생성
    """
    watchlist = WatchList.objects.create(user=current_user, name=watchlist_in.name)
    return WatchListResponse.model_validate(watchlist)


@router.get("/{watchlist_id}", response_model=WatchListResponse)
async def read_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    특정 관심목록 조회
    """
    try:
        watchlist = WatchList.objects.prefetch_related("items__stock").get(
            id=watchlist_id, user=current_user
        )
    except WatchList.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    wl_dict = WatchListResponse.model_validate(watchlist).model_dump()
    wl_dict["items"] = [
        {
            "id": item.id,
            "watchlist_id": item.watchlist_id,
            "stock_id": item.stock_id,
            "stock_code": item.stock.code,
            "stock_name": item.stock.name,
        }
        for item in watchlist.items.all()
    ]

    return WatchListResponse(**wl_dict)


@router.put("/{watchlist_id}", response_model=WatchListResponse)
async def update_watchlist(
    watchlist_id: int,
    watchlist_update: WatchListUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    관심목록 수정
    """
    try:
        watchlist = WatchList.objects.get(id=watchlist_id, user=current_user)
    except WatchList.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    update_data = watchlist_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(watchlist, field, value)

    watchlist.save()
    return WatchListResponse.model_validate(watchlist)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    관심목록 삭제
    """
    try:
        watchlist = WatchList.objects.get(id=watchlist_id, user=current_user)
    except WatchList.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    watchlist.delete()


@router.post("/{watchlist_id}/items", response_model=WatchListItemInDB, status_code=status.HTTP_201_CREATED)
async def add_watchlist_item(
    watchlist_id: int,
    item_in: WatchListItemCreate,
    current_user: User = Depends(get_current_user),
):
    """
    관심목록에 종목 추가
    """
    try:
        watchlist = WatchList.objects.get(id=watchlist_id, user=current_user)
    except WatchList.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    try:
        stock = Stock.objects.get(id=item_in.stock_id)
    except Stock.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )

    # 중복 체크
    if WatchListItem.objects.filter(watchlist=watchlist, stock=stock).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock already in watchlist",
        )

    item = WatchListItem.objects.create(watchlist=watchlist, stock=stock)

    item_dict = {
        "id": item.id,
        "watchlist_id": item.watchlist_id,
        "stock_id": item.stock_id,
        "stock_code": stock.code,
        "stock_name": stock.name,
    }

    return WatchListItemInDB(**item_dict)


@router.delete("/{watchlist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_watchlist_item(
    watchlist_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    관심목록에서 종목 제거
    """
    try:
        watchlist = WatchList.objects.get(id=watchlist_id, user=current_user)
    except WatchList.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    try:
        item = WatchListItem.objects.get(id=item_id, watchlist=watchlist)
    except WatchListItem.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    item.delete()
