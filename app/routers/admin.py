from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from ..services import crear_notificacion

from ..database import get_session
from ..models import Tramite, User
from ..schemas import TramiteOut
from ..auth import require_role

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/panel", response_model=List[TramiteOut])
def panel_tramites(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    # Ordenados por prioridad descendente (los más urgentes primero)
    tramites = session.exec(
        select(Tramite).order_by(Tramite.prioridad.desc())
    ).all()
    return tramites

@router.put("/tramites/{tramite_id}/estado")
def cambiar_estado(
    tramite_id: int,
    background_tasks: BackgroundTasks,
    nuevo_estado: str = Query(..., description="Nuevo estado del trámite"),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):

    tramite = session.get(Tramite, tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    # Validar estados permitidos
    estados_permitidos = ["recibido", "en_revision", "subsanacion", "finalizado"]
    if nuevo_estado not in estados_permitidos:
        raise HTTPException(status_code=400, detail=f"Estado no válido. Permitidos: {estados_permitidos}")
    
    tramite.estado = nuevo_estado
    tramite.fecha_actualizacion = datetime.utcnow()
    session.add(tramite)
    session.commit()
    crear_notificacion(session, tramite, nuevo_estado, background_tasks)
    session.refresh(tramite)
    # Aquí podrías enviar notificación (luego lo añadimos)
    return {"mensaje": f"Estado actualizado a '{nuevo_estado}'", "tramite": tramite}