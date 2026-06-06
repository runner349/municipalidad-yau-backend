# app/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .enums import TipoTramite

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    nombre: str
    telefono: str
    role: str = Field(default="ciudadano")  # "ciudadano" o "admin"
    is_active: bool = Field(default=True)

    tramites: List["Tramite"] = Relationship(back_populates="ciudadano")
    notificaciones: List["Notificacion"] = Relationship(back_populates="ciudadano")

class Tramite(SQLModel, table=True):
    __tablename__ = "tramites"

    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: TipoTramite # antes era str
    descripcion: str
    docs_adjuntos: int
    edad_solicitante: int
    plazo_dias: int
    es_salud: bool
    estado: str = Field(default="recibido")
    prioridad: Optional[float] = None
    error_prob: Optional[float] = None
    error_flag: bool = False
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None

    ciudadano_id: Optional[int] = Field(default=None, foreign_key="users.id")
    ciudadano: Optional[User] = Relationship(back_populates="tramites")
    
    @property
    def categoria_prioridad(self) -> str:
        if self.prioridad is None:
            return "Desconocida"
        if self.prioridad >= 8:
            return "Urgente"
        elif self.prioridad >= 6:
            return "Alta"
        elif self.prioridad >= 4:
            return "Media"
        return "Baja"

class Notificacion(SQLModel, table=True):
    __tablename__ = "notificaciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    ciudadano_id: int = Field(foreign_key="users.id")
    tramite_id: int = Field(foreign_key="tramites.id")
    mensaje: str
    tipo: str = "info"  # info, exito, advertencia, error
    leida: bool = False
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    
    ciudadano: Optional[User] = Relationship(back_populates="notificaciones")