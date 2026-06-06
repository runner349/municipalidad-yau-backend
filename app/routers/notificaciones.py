from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Notificacion, User, Tramite
from ..auth import get_current_user, require_role

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])

# Ciudadano: ver sus notificaciones
@router.get("/mis-notificaciones")
def mis_notificaciones(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    notificaciones = session.exec(
        select(Notificacion)
        .where(Notificacion.ciudadano_id == current_user.id)
        .order_by(Notificacion.fecha_creacion.desc())
    ).all()
    return notificaciones

# Marcar como leída
@router.put("/{notificacion_id}/leer")
def marcar_leida(
    notificacion_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    notificacion = session.get(Notificacion, notificacion_id)
    if not notificacion or notificacion.ciudadano_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notificacion.leida = True
    session.add(notificacion)
    session.commit()
    return {"mensaje": "Notificación marcada como leída"}

# Contador de notificaciones no leídas según el rol
@router.get("/contador")
def contador_no_leidas(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        # Solo notificaciones relevantes no leídas
        count = session.exec(
            select(Notificacion)
            .where(
                Notificacion.tipo.in_(["info", "advertencia"]),
                Notificacion.leida == False
            )
        ).all()
    else:
        # Notificaciones del ciudadano no leídas
        count = session.exec(
            select(Notificacion)
            .where(
                Notificacion.ciudadano_id == current_user.id,
                Notificacion.leida == False
            )
        ).all()
    return {"total": len(count)}

#---------
@router.get("/admin/relevantes")
def notificaciones_relevantes(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    # Obtener notificaciones relevantes con datos del trámite asociado
    statement = (
        select(Notificacion, Tramite)
        .join(Tramite, Notificacion.tramite_id == Tramite.id)
        .where(Notificacion.tipo.in_(["info", "advertencia"]))
        .order_by(Notificacion.fecha_creacion.desc())
        .limit(50)
    )
    results = session.exec(statement).all()
    
    notificaciones = []
    for notif, tramite in results:
        notificaciones.append({
            "id": notif.id,
            "tramite_id": notif.tramite_id,
            "mensaje": notif.mensaje,
            "tipo": notif.tipo,
            "leida": notif.leida,
            "fecha_creacion": notif.fecha_creacion,
            "tramite_tipo": tramite.tipo,
            "tramite_prioridad": tramite.prioridad,
            "tramite_categoria": tramite.categoria_prioridad  # propiedad del modelo
        })
    return notificaciones
#---------
# Admin: marcar notificación como leída (sin verificar dueño)
@router.put("/admin/{notificacion_id}/leer")
def admin_marcar_leida(
    notificacion_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    notificacion = session.get(Notificacion, notificacion_id)
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notificacion.leida = True
    session.add(notificacion)
    session.commit()
    return {"mensaje": "Notificación marcada como leída"}

# Admin: ver todas las notificaciones (historial)
@router.get("/admin/todas")
def todas_notificaciones(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    notificaciones = session.exec(
        select(Notificacion)
        .order_by(Notificacion.fecha_creacion.desc())
    ).all()
    return notificaciones