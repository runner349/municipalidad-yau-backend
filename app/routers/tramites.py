from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from ..services import crear_notificacion

from ..database import get_session
from ..models import Tramite, User
from ..schemas import TramiteCreate, TramiteOut
from ..auth import get_current_user
from ..ml.predictor import predecir_prioridad, predecir_error

router = APIRouter(prefix="/tramites", tags=["tramites"])

@router.post("/", response_model=TramiteOut)
def crear_tramite(
    tramite_in: TramiteCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Predecir
    prioridad = predecir_prioridad(
        tramite_in.tipo,
        tramite_in.docs_adjuntos,
        tramite_in.edad_solicitante,
        tramite_in.plazo_dias,
        tramite_in.es_salud
    )
    error_prob = predecir_error(
        tramite_in.tipo,
        tramite_in.docs_adjuntos,
        tramite_in.edad_solicitante,
        tramite_in.plazo_dias,
        tramite_in.es_salud
    )
    error_flag = error_prob > 0.5

    tramite = Tramite(
        tipo=tramite_in.tipo,
        descripcion=tramite_in.descripcion,
        docs_adjuntos=tramite_in.docs_adjuntos,
        edad_solicitante=tramite_in.edad_solicitante,
        plazo_dias=tramite_in.plazo_dias,
        es_salud=tramite_in.es_salud,
        prioridad=prioridad,
        error_prob=error_prob,
        error_flag=error_flag,
        ciudadano_id=current_user.id
    )
    session.add(tramite)
    session.commit()
    session.refresh(tramite)
    
    crear_notificacion(session, tramite, "recibido", background_tasks)
    return tramite

@router.get("/mis-tramites", response_model=List[TramiteOut])
def listar_mis_tramites(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    tramites = session.exec(
        select(Tramite).where(Tramite.ciudadano_id == current_user.id).order_by(Tramite.fecha_creacion.desc())
    ).all()
    return tramites

@router.get("/{tramite_id}", response_model=TramiteOut)
def detalle_tramite(
    tramite_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    tramite = session.get(Tramite, tramite_id)
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    if tramite.ciudadano_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    return tramite