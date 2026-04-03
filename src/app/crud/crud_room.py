from fastcrud import FastCRUD

from ..models.room import Room
from ..schemas.room import RoomCreateInternal, RoomDelete, RoomReadRow, RoomUpdate, RoomUpdateInternal

CRUDRoom = FastCRUD[Room, RoomCreateInternal, RoomUpdate, RoomUpdateInternal, RoomDelete, RoomReadRow]
crud_rooms = CRUDRoom(Room)
