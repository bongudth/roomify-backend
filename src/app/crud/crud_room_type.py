from fastcrud import FastCRUD

from ..models.room_type import RoomType
from ..schemas.room_type import (
    RoomTypeCreateInternal,
    RoomTypeDelete,
    RoomTypeRead,
    RoomTypeUpdate,
    RoomTypeUpdateInternal,
)

CRUDRoomType = FastCRUD[
    RoomType,
    RoomTypeCreateInternal,
    RoomTypeUpdate,
    RoomTypeUpdateInternal,
    RoomTypeDelete,
    RoomTypeRead,
]
crud_room_types = CRUDRoomType(RoomType)
