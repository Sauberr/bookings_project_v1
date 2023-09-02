from typing import List, Optional

from pydantic import BaseModel


class SRoom(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    services: List[str]
    price: int
    quantity: int
    image_id: int

    class Config:
        from_attributes = True


class SRoomInfo(SRoom):
    total_cost: int
    rooms_left: int

    class Config:
        from_attributes = True