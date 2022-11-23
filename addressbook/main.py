from fastapi import FastAPI, Depends, status, Response, HTTPException 
from .import schemas, models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from math import sqrt, radians, cos, acos, sin, pow, pi

app = FastAPI()
models.Base.metadata.create_all(engine)

raw_con = engine.raw_connection()
raw_con.create_function("cos", 1, cos)
raw_con.create_function("acos", 1, acos)
raw_con.create_function("sin", 1, sin)
raw_con.create_function("radians", 1, radians)
raw_con.create_function("sqrt", 1, sqrt)
raw_con.create_function("pow", 1, pow)
raw_con.create_function("pi", 1, pi)


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
def get_places(dist:int,lat:float,lng:float,db: Session = Depends(get_database_session)):
    cursor = raw_con.cursor()
   
    cursor.execute ('SELECT * FROM('
    'SELECT *,(((acos(sin(("lat"*"pi"/180)) * '
    'sin((lat*"pi"/180))+cos(("lat"*"pi"/180)) * '
    'cos((lat*"pi"/180)) * cos((("lng" - lng)*"pi"/180))))*180/"pi")*60*1.1515*1.609344) as distance FROM addrbook  WHERE distance <= "dist")')

    data = cursor.fetchall()
    return data
   


@app.get('/caldistance/')
def cal_distance(lat1:float,lng1:float,lat2:float,lng2:float,db: Session = Depends(get_database_session)):
    dist = acos(sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lng1 - lng2)) * 6371
    return dist