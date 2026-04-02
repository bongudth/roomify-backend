from fastcrud import FastCRUD

from ..models.room import Room
from ..schemas.room import RoomCreateInternal, RoomDelete, RoomRead, RoomUpdate, RoomUpdateInternal

CRUDRoom = FastCRUD[Room, RoomCreateInternal, RoomUpdate, RoomUpdateInternal, RoomDelete, RoomRead]
crud_rooms = CRUDRoom(Room)
