from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
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

@app.get("/usuarios/")
async def obtener_usuarios():
    usuarios = list(usuarios.find({}, {"_id": 1, "contraseña": 0}))  # Excluir _id y contraseña
    return {"usuarios": usuarios}

@app.get("/")
def read_root():
    return {"message": "¡Conectado a MongoDB!"}
