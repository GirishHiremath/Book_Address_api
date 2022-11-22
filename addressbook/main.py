from fastapi import FastAPI, Depends, status, Response, HTTPException 
from .import schemas, models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


app = FastAPI()
models.Base.metadata.create_all(engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/",status_code=status.HTTP_200_OK)
def read(db: Session = Depends(get_database_session)):
    records = db.query(models.AddreBook).all()
    return records

@app.post('/addrcreat', status_code=status.HTTP_201_CREATED)
def create(request: schemas.AddressBook, db: Session = Depends(get_database_session)):
    new_addr= models.AddreBook(place=request.place, lat=request.lat, lng=request.lng) 
    db.add(new_addr)
    db.commit()
    db.refresh(new_addr)
    return new_addr

@app.get('/{id}', status_code=status.HTTP_200_OK)
def show(id, response:Response, db: Session = Depends(get_database_session)):
    adder= db.query(models.AddreBook).filter(models.AddreBook.id == id).first()
    if not adder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                        detail=f'Address not found for id {id}')
        
    return adder


@app.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id, request: schemas.AddressBook, db: Session = Depends(get_database_session)):
    adder= db.query(models.AddreBook).filter(models.AddreBook.id == id)
    if not adder.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                           detail=f'Address with {id} not found')
    adder.update({'place': request.place, 'lat': request.lat, 'lng': request.lng})
    db.commit()
    
    return 'Updated'


@app.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destory(id, db: Session = Depends(get_database_session)):
    adder= db.query(models.AddreBook).filter(models.AddreBook.id == id)
    if not adder.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f'Address with {id} not found')
    adder.delete(synchronize_session=False)
    db.commit()
    return 'Done'


@app.get('/distance/')
def get_places(dist,lat,lng,db: Session = Depends(get_database_session)):
   data=db.query(models.AddreBook).from_statement(
    text('SELECT * FROM addrbook WHERE acos(sin("lat") * sin("models.addreBook.lat") + cos("lat") * cos("models.addreBook.lat") * cos("models.addreBook.lng" - ("lng"))) * 6371 <= "dist"')).all()
   return data
