import time

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Laptop

app = FastAPI()


class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database():
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as db:
                if db.scalar(select(Laptop.id).limit(1)) is None:
                    db.add_all([
                        Laptop(marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True),
                        Laptop(marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False),
                        Laptop(marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True),
                    ])
                    db.commit()
            return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("No se pudo conectar con MySQL")


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def root():
    return {"mensaje": "API del laboratorio de cómputo"}


@app.get("/laptops")
def get_laptops(db: Session = Depends(get_db)):
    return db.scalars(select(Laptop).order_by(Laptop.id)).all()


@app.get("/laptops/disponibles")
def get_available_laptops(db: Session = Depends(get_db)):
    return db.scalars(
        select(Laptop).where(Laptop.disponible.is_(True)).order_by(Laptop.id)
    ).all()


@app.get("/laptops/{laptop_id}")
def get_laptop(laptop_id: int, db: Session = Depends(get_db)):
    laptop = db.get(Laptop, laptop_id)
    if laptop is None:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop


@app.post("/laptops")
def create_laptop(laptop: LaptopCreate, db: Session = Depends(get_db)):
    nueva = Laptop(
        marca=laptop.marca,
        modelo=laptop.modelo,
        ram_gb=laptop.ram_gb,
        disponible=True,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva
