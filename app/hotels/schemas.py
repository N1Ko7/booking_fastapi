from typing import List, Optional

from pydantic import BaseModel


class SHotel(BaseModel):
    id: int
    name: str
    location: str
    services: List[str]
    rooms_quantity: int
    image_id: Optional[int] = None

    class Config:
        from_attributes = True


class SHotelWithRoomsLeft(SHotel):
    rooms_left: int
