from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType
from .email_config import conf
from .models import Notificacion, Tramite, User
from sqlmodel import Session, select

def crear_notificacion(
    session: Session,
    tramite: Tramite,
    estado: str,
    background_tasks: BackgroundTasks | None = None
):
    # Categoría de prioridad
    if tramite.prioridad is None:
        categoria = "Desconocida"
    elif tramite.prioridad >= 8:
        categoria = "Urgente"
    elif tramite.prioridad >= 6:
        categoria = "Alta"
    elif tramite.prioridad >= 4:
        categoria = "Media"
    else:
        categoria = "Baja"

    tipo_tramite = tramite.tipo.replace('_', ' ').title()

    if estado == "recibido":
        mensaje = f"Nuevo trámite de {tipo_tramite} (Prioridad: {categoria}) recibido."
        tipo_notif = "info"
    elif estado == "en_revision":
        mensaje = f"Trámite de {tipo_tramite} (Prioridad: {categoria}) en revisión."
        tipo_notif = "info"
    elif estado == "subsanacion":
        mensaje = f"Trámite de {tipo_tramite} (Prioridad: {categoria}) requiere subsanación."
        tipo_notif = "advertencia"
    elif estado == "finalizado":
        mensaje = f"Trámite de {tipo_tramite} (Prioridad: {categoria}) ha finalizado."
        tipo_notif = "exito"
    else:
        mensaje = f"El estado del trámite de {tipo_tramite} cambió a '{estado}'."
        tipo_notif = "info"

    notificacion = Notificacion(
        ciudadano_id=tramite.ciudadano_id,
        tramite_id=tramite.id,
        mensaje=mensaje,
        tipo=tipo_notif
    )
    session.add(notificacion)
    session.commit()

    # Enviar correo si hay background_tasks y el ciudadano tiene email
    if background_tasks:
        ciudadano = session.get(User, tramite.ciudadano_id)
        if ciudadano and ciudadano.email:
            asunto = f"[Trámite #{tramite.id}] {categoria} - {tipo_tramite} ({estado.replace('_', ' ')})"
            background_tasks.add_task(enviar_correo, ciudadano.email, asunto, mensaje, tramite.id)

async def enviar_correo(destinatario: str, asunto: str, mensaje: str, tramite_id: int):
    html = f"""
    <h2>Municipalidad de Yau - Actualización de trámite</h2>
    <p>{mensaje}</p>
    <p><strong>Trámite ID:</strong> {tramite_id}</p>
    <p>Consulte el estado en: <a href="http://localhost:5173/tramite/{tramite_id}">nuestro portal</a></p>
    <hr>
    <p><small>Este es un mensaje automático, por favor no responda.</small></p>
    """
    message = MessageSchema(
        subject=asunto,
        recipients=[destinatario],
        body=html,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)