# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .enums import TipoTramite

# ----------------- Usuarios -----------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    telefono: str
    role: str = "ciudadano"

class UserOut(BaseModel):
    id: int
    email: str
    nombre: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None   # user id como string

# ----------------- Trámites -----------------
class TramiteCreate(BaseModel):
    tipo: TipoTramite   # antes era str
    descripcion: str
    docs_adjuntos: int
    edad_solicitante: int
    plazo_dias: int
    es_salud: bool

class TramiteOut(BaseModel):
    id: int
    tipo: str
    descripcion: str
    estado: str
    prioridad: Optional[float]
    error_prob: Optional[float]
    error_flag: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    ciudadano_id: int
    categoria_prioridad: str