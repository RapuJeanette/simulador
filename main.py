from datetime import date, datetime
from email import errors
from typing import List, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from bson.objectid import ObjectId 
from pymongo import MongoClient
import bcrypt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Permite solicitudes desde este origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)

client = MongoClient('mongodb+srv://rapupena2909:Hola2020@ecommerce.t4bf6tt.mongodb.net/?retryWrites=true&w=majority&appName=ecommerce/')
db = client['simulador']
usuarios= db['user']

class Usuario(BaseModel):
    nombre: str
    correo: EmailStr
    password: str

# Helper para hash de contraseñas
def hash_contraseña(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Endpoint para crear un nuevo usuario
@app.post("/usuarios/")
async def crear_usuario(usuario: Usuario):
    if usuarios.find_one({"correo": usuario.correo}):
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    usuario_con_hashed_password = usuario.dict()
    usuario_con_hashed_password["password"] = hash_contraseña(usuario.password)
    
    usuarios.insert_one(usuario_con_hashed_password)
    
    return {"message": "Usuario creado exitosamente"}

class DoctorCreate(BaseModel):
    telefono: str
    especialidad: str
    disponibilidad: str

# Modelo para responder con 'id'
class Doctor(BaseModel):
    id: Optional[str] = Field(None)
    telefono: str
    especialidad: str
    disponibilidad: str

db = client['simulador']
doctores = db['doctor']

@app.post("/doctores/", response_model=Doctor)
def crear_doctor(doctor: DoctorCreate):
    nuevo_doctor = doctor.dict()  # Convertir el doctor a diccionario
    nuevo_doctor['id'] = str(uuid4())  # Generar ID único
    doctores.insert_one(nuevo_doctor)  # Insertar en MongoDB
    return nuevo_doctor 

@app.get("/doctores/", response_model=List[Doctor])
async def obtener_doctores():
    try:
        doctore = list(doctores.find()) 
        for doctor in doctore:
            doctor['id'] = str(doctor['_id']) 
        return doctore
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/doctores/{doctor_id}", response_model=Doctor)
async def obtener_doctor(doctor_id: str):
    doctor = doctores.find_one({"_id": ObjectId(doctor_id)})  # Buscar el doctor por _id
    if doctor:
        doctor['id'] = str(doctor['_id'])  # Convertir ObjectId a string
        del doctor['_id']  # Eliminar el campo _id
        return doctor
    raise HTTPException(status_code=404, detail="Doctor no encontrado")

# Actualizar un doctor
@app.put("/doctores/{doctor_id}", response_model=Doctor)
async def actualizar_doctor(doctor_id: str, doctor_actualizado: Doctor):
    result = doctores.update_one(
        {"_id": ObjectId(doctor_id)},  # Buscar por _id
        {"$set": doctor_actualizado.dict()}  # Excluir el campo id del update
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    
    # Obtener el doctor actualizado
    doctor_actualizado_db = doctores.find_one({"_id": ObjectId(doctor_id)})
    doctor_actualizado_db['id'] = str(doctor_actualizado_db['_id'])
    del doctor_actualizado_db['_id']
    
    return doctor_actualizado_db

# Eliminar un doctor
@app.delete("/doctores/{doctor_id}")
async def eliminar_doctor(doctor_id: str):
    result = doctores.delete_one({"_id": ObjectId(doctor_id)})  # Eliminar por _id
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    return {"mensaje": "Doctor eliminado"}

class Pago(BaseModel):
    id: Optional[str] = Field(None)
    monto: float
    estado: str  # Puede ser 'pendiente' o 'completado'
    fecha: datetime

db = client['simulador']
pagos_db= db['pago']

@app.post("/pagos/", response_model=Pago)
def crear_pago(pago: Pago):
    nuevo_pago = pago.dict()  
    if isinstance(nuevo_pago['fecha'], date):  # Si es un objeto date, convertir a datetime
        nuevo_pago['fecha'] = datetime.combine(nuevo_pago['fecha'], datetime.min.time())
    pagos_db.insert_one(nuevo_pago)
    nuevo_pago['id'] = str(nuevo_pago['_id']) 
    return nuevo_pago

@app.get("/pagos/", response_model=List[Pago])
async def obtener_pagos():
      try:
          pagos = list(db.pago.find())
          for pago in pagos:
             pago['id'] = str(pago['_id'])  
          return pagos
      except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pagos/{pago_id}", response_model=Pago)
async def obtener_pago_por_id(pago_id: str):
    pago = pagos_db.find_one({"_id": ObjectId(pago_id)})
    if pago:
        pago['id'] = str(pago['_id'])  # Convertir ObjectId a string
        return pago
    raise HTTPException(status_code=404, detail="Doctor no encontrado")

@app.put("/pagos/{pago_id}", response_model=Pago)
async def actualizar_pago(pago_id: str, pago_actualizado: Pago):
    result = pagos_db.update_one(
        {"_id": ObjectId(pago_id)},
        {"$set": pago_actualizado.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException (status_code=404, detail="Pago no encontrado")
    
    pago_actualizado_db = pagos_db.find_one({"_id":
        ObjectId(pago_id)})
    pago_actualizado_db['id'] = str(pago_actualizado_db['_id'])
    return pago_actualizado_db

# Eliminar un pago por ID
@app.delete("/pagos/{pago_id}")
async def eliminar_pago(pago_id: str):
    result = pagos_db.delete_one({"_id": ObjectId(pago_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    return {"mensaje": "Doctor eliminado"}

@app.get("/")
def read_root():
    return {"message": "¡Conectado a MongoDB!"}
