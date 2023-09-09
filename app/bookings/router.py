from datetime import date

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from pydantic import TypeAdapter

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

# from fastapi import BackgroundTasks


router = APIRouter(
    prefix='/bookings',
    tags=['Bookings'],
)


@router.get('')
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post('')
@version(1)
async def add_booking(
        # background_tasks: BackgroundTasks,
        room_id: int,
        date_from: date,
        date_to: date,
        user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
    booking_obj = TypeAdapter(SBooking)
    booking_dict = booking_obj.validate_python(booking).model_dump()
    # With celery
    send_booking_confirmation_email.delay(booking_dict, user.email)
    # With background_tasks
    # background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    return booking_dict


@router.delete('/{booking_id}')
async def remove_booking(
        booking_id: int,
        current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user)


