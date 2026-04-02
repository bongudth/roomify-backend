from fastcrud import FastCRUD

from ..models.floor import Floor
from ..schemas.floor import FloorCreateInternal, FloorDelete, FloorRead, FloorUpdate, FloorUpdateInternal

CRUDFloor = FastCRUD[Floor, FloorCreateInternal, FloorUpdate, FloorUpdateInternal, FloorDelete, FloorRead]
crud_floors = CRUDFloor(Floor)
