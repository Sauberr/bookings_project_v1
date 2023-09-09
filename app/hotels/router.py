from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotel, SHotelInfo

router = APIRouter(
    prefix='/hotels',
    tags=['Hotels']
)


@router.get('/{location}', status_code=200)
@cache(expire=20)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date = Query(..., description=f'For example , {datetime.now().date()}'),
    date_to: date = Query(..., description=f'For example, {(datetime.now() + timedelta(days=14)).date()}'),
) -> List[SHotelInfo]:
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    return hotels


@router.get('/id/{hotels_id}', status_code=200)
async def get_hotels_by_id(
        hotel_id: int
) -> Optional[SHotel]:
    return await HotelDAO.find_one_or_none(id=hotel_id)