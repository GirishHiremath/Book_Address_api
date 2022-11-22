from pydantic import BaseModel

class AddressBook(BaseModel):
    place: str
    lat: float
    lng: float