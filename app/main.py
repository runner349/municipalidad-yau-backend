# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_and_tables
from .routers import auth, tramites, admin, notificaciones

app = FastAPI(title="Municipalidad Yau - Sistema de Trámites")

# CORS (ajusta los orígenes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al iniciar (solo desarrollo)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Incluir routers
app.include_router(auth.router)
app.include_router(tramites.router)
app.include_router(admin.router)
app.include_router(notificaciones.router)

@app.get("/")
def root():
    return {"mensaje": "API de trámites funcionando"}