"""Servicio FastAPI protegido y canal web de chat para el sistema multi-agente A2A."""

from __future__ import annotations

import hmac
import logging
import os
import re
import uuid
from datetime import datetime

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Security, status
from fastapi.responses import HTMLResponse, Response
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

load_dotenv(override=True)

from src.coordinador import catalogo
from src.coordinador.cliente import obtener_cliente, preguntar
from src.coordinador.graph import consultar_detallado

URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8007")

app = FastAPI(
    title="Servicio FastAPI y Canal Web - Agentes A2A",
    description=(
        "API protegida por token y canal web de chat que conecta con el "
        "Coordinador y los agentes especialistas mediante el protocolo A2A."
    ),
    version="1.0.0",
)

esquema_bearer = HTTPBearer(auto_error=False, description="Ingresa tu TOKEN_ACCESO configurado en .env")
esquema_api_key = APIKeyHeader(name="X-API-Key", auto_error=False, description="Alternativa: TOKEN_ACCESO en header X-API-Key")


def _obtener_token_esperado() -> str:
    """Obtiene el token configurado en el servidor desde variables de entorno."""
    return (os.getenv("TOKEN_ACCESO") or "").strip()


def _obtener_clave_elevenlabs() -> str:
    """Obtiene la clave de ElevenLabs desde .env (VITE_ELEVENLABS_API_KEY), recargando .env por si cambió."""
    load_dotenv(override=True)
    return (
        os.getenv("VITE_ELEVENLABS_API_KEY")
        or os.getenv("ELEVENLABS_API_KEY")
        or ""
    ).strip()


def _limpiar_texto_para_voz(texto: str) -> str:
    """Limpia símbolos Markdown para que ElevenLabs lea el texto con naturalidad."""
    limpio = re.sub(r"\[([^\]]+)\]", r"\1: ", texto or "")
    limpio = re.sub(r"[*_`#>-]+", " ", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    # Limitar a 1800 caracteres para proteger cuota y latencia de ElevenLabs
    return limpio[:1800]


async def sintetizar_voz_elevenlabs(texto: str) -> bytes:
    """Convierte el texto de respuesta en audio MP3 consultando la API de ElevenLabs."""
    clave_voz = _obtener_clave_elevenlabs()
    if not clave_voz:
        raise ValueError(
            "VITE_ELEVENLABS_API_KEY no está configurada en el archivo .env del servidor."
        )

    texto_limpio = _limpiar_texto_para_voz(texto)
    if not texto_limpio:
        raise ValueError("El texto para convertir a voz está vacío.")

    voice_id = (os.getenv("ELEVENLABS_VOICE_ID") or "IKne3meq5aSn9XLyUdCD").strip()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    encabezados = {
        "xi-api-key": clave_voz,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    cuerpo = {
        "text": texto_limpio,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    async with httpx.AsyncClient(timeout=45.0) as cliente:
        respuesta = await cliente.post(url, headers=encabezados, json=cuerpo)
        if respuesta.status_code != 200:
            detalle = respuesta.text.replace(chr(10), " ").strip()[:160]
            raise RuntimeError(
                f"ElevenLabs respondió HTTP {respuesta.status_code}: {detalle}"
            )
        return respuesta.content


def _hora_actual() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def verificar_acceso(
    credenciales: HTTPAuthorizationCredentials | None = Security(esquema_bearer),
    x_api_key: str | None = Security(esquema_api_key),
    authorization: str | None = Header(default=None, include_in_schema=False),
) -> str:
    """Valida el token de acceso en el servidor (Bearer o X-API-Key).

    Registra en consola tanto los accesos permitidos como los rechazados
    sin imprimir el token real en los logs.
    """
    token_esperado = _obtener_token_esperado()
    if not token_esperado:
        print(
            f"[{_hora_actual()}] [CONFIGURACION] Error: TOKEN_ACCESO no está configurado en .env"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración: TOKEN_ACCESO no está definido en el servidor.",
        )

    token_recibido = ""
    if credenciales and credenciales.credentials:
        token_recibido = credenciales.credentials.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        token_recibido = authorization[7:].strip()
    elif x_api_key:
        token_recibido = x_api_key.strip()

    if not token_recibido:
        print(
            f"[{_hora_actual()}] [ACCESO RECHAZADO] Motivo: solicitud sin token de autorización."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso rechazado: falta el token de autorización (use Authorization: Bearer <token> o X-API-Key).",
        )

    if not hmac.compare_digest(token_recibido, token_esperado):
        print(
            f"[{_hora_actual()}] [ACCESO RECHAZADO] Motivo: token inválido (oculto por seguridad)."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso rechazado: el token proporcionado no es válido.",
        )

    print(f"[{_hora_actual()}] [ACCESO PERMITIDO] Token validado correctamente.")
    return "autorizado"


class PeticionChat(BaseModel):
    mensaje: str = Field(..., description="Pregunta o solicitud del usuario.")
    context_id: str | None = Field(
        default=None,
        description="Identificador de sesión para conservar memoria conversacional.",
    )


class PeticionVoz(BaseModel):
    texto: str = Field(..., description="Texto de la respuesta del agente que se convertirá en audio MP3.")


class _FiltroRuidoScanner(logging.Filter):
    """Oculta del log de consola el ruido de escáneres locales y cierre de socket en Windows."""

    def filter(self, record: logging.LogRecord) -> bool:
        mensaje = record.getMessage()
        if '"GET /health ' in mensaje or '"GET /v1/models ' in mensaje:
            return False
        if "_ProactorBasePipeTransport._call_connection_lost" in mensaje:
            return False
        if record.exc_info and record.exc_info[1] is not None:
            if isinstance(record.exc_info[1], ConnectionResetError):
                return False
        return True


logging.getLogger("uvicorn.access").addFilter(_FiltroRuidoScanner())
logging.getLogger("asyncio").addFilter(_FiltroRuidoScanner())


@app.on_event("startup")
async def al_arrancar() -> None:
    logging.getLogger("uvicorn.access").addFilter(_FiltroRuidoScanner())
    logging.getLogger("asyncio").addFilter(_FiltroRuidoScanner())
    await catalogo.descubrir()
    token_configurado = "SÍ" if _obtener_token_esperado() else "NO (configure TOKEN_ACCESO en .env)"
    print(
        f"[{_hora_actual()}] [INICIO] Servidor FastAPI + Canal Web listo | "
        f"Agentes A2A descubiertos: {len(catalogo.CATALOGO)} | "
        f"Control de acceso activo: {token_configurado}"
    )


@app.get("/salud")
@app.get("/health", include_in_schema=False)
@app.get("/v1/models", include_in_schema=False)
async def salud() -> dict:
    """Ruta pública de salud del servicio."""
    return {
        "ok": True,
        "servicio": "FastAPI + Canal Web A2A",
        "agentes_descubiertos": len(catalogo.CATALOGO),
        "acceso_protegido": bool(_obtener_token_esperado()),
        "voz_elevenlabs_configurada": bool(_obtener_clave_elevenlabs()),
    }


@app.get("/agentes")
async def listar_agentes(
    actualizar: bool = Query(default=False, description="Si es true, vuelve a descubrir los agentes A2A."),
    _acceso: str = Depends(verificar_acceso),
) -> list[dict]:
    """Devuelve la lista de agentes A2A descubiertos (requiere token de acceso)."""
    if actualizar or not catalogo.CATALOGO:
        await catalogo.descubrir()
    return [
        {"nombre": a["nombre"], "descripcion": a["descripcion"], "url": a["url"]}
        for a in catalogo.CATALOGO
    ]


def _extraer_agentes_de_respuesta(respuesta: str) -> list[str]:
    """Extrae los nombres de agentes entre corchetes [Agente ...] de la respuesta A2A."""
    encontrados = re.findall(r"\[([^\]]+)\]", respuesta or "")
    ignorar = {
        "Conclusión integrada del Coordinador",
        "Coordinador - Datos faltantes",
    }
    agentes: list[str] = []
    for nombre in encontrados:
        if nombre not in ignorar and nombre not in agentes:
            agentes.append(nombre)
    return agentes


async def _consultar_via_coordinador_a2a(texto: str, context_id: str) -> dict | None:
    """Intenta enviar la consulta al servidor A2A del Coordinador (puerto 8007).

    Devuelve el diccionario de respuesta si el servidor del Coordinador está activo,
    o None si no está levantado para usar el grafo local como respaldo.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as cliente_salud:
            r_salud = await cliente_salud.get(f"{URL_COORDINADOR}/salud")
            if r_salud.status_code != 200:
                return None
    except Exception:  # noqa: BLE001
        return None

    print(
        f"[{_hora_actual()}] [A2A -> COORDINADOR] Enviando consulta al servidor Coordinador en {URL_COORDINADOR} | context_id={context_id}"
    )
    cliente_coord = await obtener_cliente(URL_COORDINADOR)
    respuesta = await preguntar(cliente_coord, texto, context_id)
    agentes = _extraer_agentes_de_respuesta(respuesta)
    faltan_datos = "[Coordinador - Datos faltantes]" in respuesta

    return {
        "context_id": context_id,
        "respuesta": respuesta,
        "agentes": agentes,
        "motivo": f"Procesado por servidor Coordinador A2A ({URL_COORDINADOR})",
        "faltan_datos": faltan_datos,
        "aportes": [],
    }


async def _procesar_consulta(peticion: PeticionChat) -> dict:
    """Valida la entrada, invoca al coordinador A2A y estructura la respuesta."""
    texto = (peticion.mensaje or "").strip()
    if not texto:
        print(f"[{_hora_actual()}] [ENTRADA INVALIDA] Mensaje vacío rechazado.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrada inválida: el mensaje no puede estar vacío.",
        )

    if len(texto) > 2000:
        print(f"[{_hora_actual()}] [ENTRADA INVALIDA] Mensaje excede límite de 2000 caracteres.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrada inválida: el mensaje supera el límite máximo de 2000 caracteres.",
        )

    context_id = peticion.context_id or str(uuid.uuid4())
    print(
        f"[{_hora_actual()}] [SOLICITUD] context_id={context_id} | mensaje='{texto}'"
    )

    try:
        # Si el servidor A2A del Coordinador (8007) está corriendo, le delegamos por A2A;
        # si no está corriendo, usamos el grafo local del coordinador.
        detalle = await _consultar_via_coordinador_a2a(texto, context_id)
        if detalle is None:
            detalle = await consultar_detallado(texto, context_id)

        respuesta = detalle.get("respuesta", "")
        agentes = detalle.get("agentes", [])
        motivo = detalle.get("motivo", "")
        faltan_datos = detalle.get("faltan_datos", False)
        aportes = detalle.get("aportes", [])

        # Detectar si la respuesta corresponde a un error de proveedor o agente caído.
        es_error = respuesta.startswith("Error:") or "No se pudo consultar al agente" in respuesta
        es_fuera_alcance = respuesta.startswith("Fuera de alcance:")

        estado_operacion = "completado"
        if es_error:
            estado_operacion = "error_proveedor_o_agente"
        elif faltan_datos:
            estado_operacion = "datos_faltantes"
        elif es_fuera_alcance:
            estado_operacion = "fuera_de_alcance"

        print(
            f"[{_hora_actual()}] [RESPUESTA] context_id={context_id} | "
            f"estado={estado_operacion} | agentes={agentes}"
        )

        return {
            "ok": not es_error,
            "estado": estado_operacion,
            "context_id": context_id,
            "agentes_participantes": agentes,
            "motivo_seleccion": motivo,
            "faltan_datos": faltan_datos,
            "aportes": aportes,
            "respuesta": respuesta,
        }
    except Exception as error:  # noqa: BLE001 - Regla 4: error en una sola línea sin stack trace
        mensaje_error = str(error).replace(chr(10), " ").strip()
        print(f"[{_hora_actual()}] [ERROR] Fallo procesando consulta: {mensaje_error}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al procesar la consulta con los agentes: {mensaje_error}",
        ) from None


@app.post("/chat")
async def chat(
    peticion: PeticionChat,
    _acceso: str = Depends(verificar_acceso),
) -> dict:
    """Endpoint protegido usado por el frontend web de chat."""
    return await _procesar_consulta(peticion)


@app.post("/api/consultar")
async def api_consultar(
    peticion: PeticionChat,
    _acceso: str = Depends(verificar_acceso),
) -> dict:
    """Endpoint REST protegido del Servicio FastAPI para clientes externos."""
    return await _procesar_consulta(peticion)


@app.post("/api/voz")
async def api_voz(
    peticion: PeticionVoz,
    _acceso: str = Depends(verificar_acceso),
) -> Response:
    """Genera el audio MP3 de la respuesta usando ElevenLabs (protegido por TOKEN_ACCESO)."""
    try:
        print(
            f"[{_hora_actual()}] [ELEVENLABS] Generando audio MP3 para respuesta ({len(peticion.texto or '')} caracteres)..."
        )
        audio_bytes = await sintetizar_voz_elevenlabs(peticion.texto)
        print(
            f"[{_hora_actual()}] [ELEVENLABS] Audio generado correctamente ({len(audio_bytes)} bytes)."
        )
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as error:  # noqa: BLE001 - Regla 4: error en una sola línea sin stack trace
        mensaje_err = str(error).replace(chr(10), " ").strip()
        print(f"[{_hora_actual()}] [ELEVENLABS ERROR] {mensaje_err}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al generar audio con ElevenLabs: {mensaje_err}",
        ) from None


@app.get("/", response_class=HTMLResponse)
async def pagina() -> str:
    """Entrega la interfaz web de chat (sin incluir secretos ni claves en el HTML)."""
    return HTML_PAGINA


HTML_PAGINA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Canal Web y Servicio FastAPI - Agentes A2A</title>
<style>
  :root {
    --bg: #f8fafc;
    --panel: #ffffff;
    --border: #e2e8f0;
    --primary: #1e40af;
    --primary-light: #dbeafe;
    --text: #0f172a;
    --muted: #475569;
    --ok-bg: #dcfce7;
    --ok-text: #166534;
    --err-bg: #fee2e2;
    --err-text: #991b1b;
    --warn-bg: #fef3c7;
    --warn-text: #92400e;
  }
  * { box-sizing: border-box; }
  body {
    font-family: system-ui, -apple-system, sans-serif;
    margin: 0;
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--bg);
    color: var(--text);
  }
  header {
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }
  .titulo-app {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .titulo-app h1 {
    font-size: 16px;
    margin: 0;
  }
  .badge-entorno {
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 999px;
    background: #e0e7ff;
    color: #1e3a8a;
  }
  .control-acceso {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .control-acceso label {
    font-size: 13px;
    font-weight: 600;
  }
  .control-acceso input {
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 13px;
    width: 210px;
  }
  .btn {
    padding: 7px 12px;
    border-radius: 6px;
    border: 1px solid transparent;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    background: var(--primary);
    color: white;
  }
  .btn-secundario {
    background: white;
    color: var(--text);
    border-color: var(--border);
  }
  .estado-acceso {
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    background: #f1f5f9;
    color: var(--muted);
  }
  .estado-acceso.ok { background: var(--ok-bg); color: var(--ok-text); }
  .estado-acceso.err { background: var(--err-bg); color: var(--err-text); }
  .contenedor {
    flex: 1;
    display: flex;
    overflow: hidden;
  }
  aside {
    width: 290px;
    border-right: 1px solid var(--border);
    padding: 14px;
    overflow-y: auto;
    background: var(--panel);
  }
  aside h2 {
    font-size: 14px;
    margin: 0 0 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
  }
  .card h3 { margin: 0 0 4px; font-size: 13px; color: var(--primary); }
  .card p { margin: 0 0 6px; font-size: 12px; color: var(--muted); line-height: 1.35; }
  .card code { font-size: 11px; color: #334155; background: #e2e8f0; padding: 2px 5px; border-radius: 4px; }
  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  #mensajes {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .msg {
    padding: 12px 14px;
    border-radius: 10px;
    max-width: 82%;
    white-space: pre-wrap;
    line-height: 1.45;
    font-size: 14px;
    border: 1px solid transparent;
  }
  .user {
    background: var(--primary-light);
    border-color: #bfdbfe;
    margin-left: auto;
  }
  .agent {
    background: var(--panel);
    border-color: var(--border);
    margin-right: auto;
  }
  .agent.error {
    background: var(--err-bg);
    border-color: #fecaca;
    color: var(--err-text);
  }
  .agent.warn {
    background: var(--warn-bg);
    border-color: #fde68a;
    color: var(--warn-text);
  }
  .meta-msg {
    font-size: 11px;
    font-weight: 600;
    color: var(--muted);
    margin-bottom: 6px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .tag-a2a {
    background: #e0f2fe;
    color: #0369a1;
    padding: 2px 6px;
    border-radius: 4px;
  }
  .barra-audio {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px dashed var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .btn-voz {
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    color: #1e293b;
    cursor: pointer;
  }
  .btn-voz:hover {
    background: #e2e8f0;
  }
  .barra-audio audio {
    height: 32px;
    max-width: 280px;
  }
  .check-voz {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
    cursor: pointer;
    user-select: none;
  }
  .loading-box {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: var(--primary);
    font-weight: 600;
  }
  .spinner {
    width: 18px;
    height: 18px;
    border: 3px solid #bfdbfe;
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: girar 0.8s linear infinite;
    flex-shrink: 0;
  }
  @keyframes girar {
    to { transform: rotate(360deg); }
  }
  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  form {
    display: flex;
    padding: 12px 16px;
    border-top: 1px solid var(--border);
    background: var(--panel);
    gap: 8px;
  }
  #input {
    flex: 1;
    padding: 10px 12px;
    font-size: 14px;
    border: 1px solid var(--border);
    border-radius: 6px;
  }
</style>
</head>
<body>
<header>
  <div class="titulo-app">
    <h1>Coordinador y Agentes A2A</h1>
    <span class="badge-entorno" id="badge-fecha">LOCAL</span>
  </div>
  <div class="control-acceso">
    <label for="token">Token de acceso:</label>
    <input id="token" type="password" placeholder="Ingresa TOKEN_ACCESO..." autocomplete="off" />
    <button type="button" class="btn" id="btn-conectar">Verificar acceso</button>
    <button type="button" class="btn btn-secundario" id="btn-nueva">Nueva sesión</button>
    <label class="check-voz" title="Genera y reproduce automáticamente la voz con ElevenLabs al recibir cada respuesta">
      <input type="checkbox" id="auto-voz" checked />
      🔊 Voz automática (ElevenLabs)
    </label>
    <span id="estado-acceso" class="estado-acceso">Sin verificar</span>
  </div>
</header>

<div class="contenedor">
  <aside>
    <h2>
      <span>Catálogo A2A</span>
      <button type="button" class="btn btn-secundario" id="btn-redescubrir" style="padding:3px 8px;font-size:11px;">Actualizar</button>
    </h2>
    <div id="lista-agentes">Ingresa el token y pulsa "Verificar acceso" para consultar el catálogo A2A.</div>
  </aside>

  <main>
    <div id="mensajes"></div>
    <form id="form">
      <input id="input" placeholder="Escribe tu consulta (ej. receta de brownie para 16 personas y 2 canciones bailables de los 80)..." autocomplete="off" />
      <button type="submit" class="btn" id="btn-enviar">Enviar consulta</button>
    </form>
  </main>
</div>

<script>
  let contextId = null;
  const mensajes = document.getElementById('mensajes');
  const form = document.getElementById('form');
  const input = document.getElementById('input');
  const btnEnviar = document.getElementById('btn-enviar');
  const tokenInput = document.getElementById('token');
  const estadoAcceso = document.getElementById('estado-acceso');
  const badgeFecha = document.getElementById('badge-fecha');

  function mostrarLoading(textoInicial = 'Consultando al Coordinador y agentes A2A...') {
    const div = document.createElement('div');
    div.className = 'msg agent';
    let segundos = 0;
    div.innerHTML = '<div class="loading-box"><div class="spinner"></div><span class="texto-loading">' + textoInicial + ' (0s)</span></div>';
    mensajes.appendChild(div);
    mensajes.scrollTop = mensajes.scrollHeight;
    const spanTexto = div.querySelector('.texto-loading');
    const intervalo = setInterval(() => {
      segundos += 1;
      if (spanTexto) {
        spanTexto.textContent = textoInicial + ' (' + segundos + 's)';
      }
    }, 1000);
    return function quitarLoading() {
      clearInterval(intervalo);
      if (div.parentNode) {
        div.parentNode.removeChild(div);
      }
    };
  }

  const hoy = new Date().toISOString().slice(0, 10);
  badgeFecha.textContent = 'ENTORNO: LOCAL | ' + hoy;

  function obtenerHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const t = tokenInput.value.trim();
    if (t) {
      headers['Authorization'] = 'Bearer ' + t;
    }
    return headers;
  }

  function actualizarBadgeAcceso(ok, texto) {
    estadoAcceso.textContent = texto;
    estadoAcceso.className = 'estado-acceso ' + (ok ? 'ok' : 'err');
  }

  async function cargarAgentes(forzar = false) {
    const cont = document.getElementById('lista-agentes');
    try {
      const url = forzar ? '/agentes?actualizar=true' : '/agentes';
      const r = await fetch(url, { headers: obtenerHeaders() });
      const data = await r.json();
      if (!r.ok) {
        actualizarBadgeAcceso(false, 'Acceso rechazado (' + r.status + ')');
        cont.innerHTML = '<div class="card"><p style="color:#991b1b;font-weight:600;">' + (data.detail || 'Acceso rechazado') + '</p></div>';
        return false;
      }
      actualizarBadgeAcceso(true, 'Acceso autorizado (200)');
      cont.innerHTML = '';
      data.forEach(a => {
        const div = document.createElement('div');
        div.className = 'card';
        div.innerHTML = '<h3>' + a.nombre + '</h3><p>' + a.descripcion + '</p><code>A2A: ' + a.url + '</code>';
        cont.appendChild(div);
      });
      if (data.length === 0) {
        cont.textContent = 'Sin agentes remotos descubiertos. Verifica que los agentes estén ejecutándose.';
      }
      return true;
    } catch (err) {
      actualizarBadgeAcceso(false, 'Error de red');
      cont.textContent = 'No se pudo conectar con el servidor FastAPI.';
      return false;
    }
  }

  function agregarMensaje(texto, clase, metaTexto = '', conAudio = false) {
    const div = document.createElement('div');
    div.className = 'msg ' + clase;
    if (metaTexto) {
      const meta = document.createElement('div');
      meta.className = 'meta-msg';
      meta.innerHTML = metaTexto;
      div.appendChild(meta);
    }
    const cuerpo = document.createElement('div');
    cuerpo.textContent = texto;
    div.appendChild(cuerpo);

    if (conAudio && texto) {
      const barraAudio = document.createElement('div');
      barraAudio.className = 'barra-audio';
      const btnVoz = document.createElement('button');
      btnVoz.type = 'button';
      btnVoz.className = 'btn-voz';
      btnVoz.textContent = '🔊 Escuchar respuesta (ElevenLabs)';
      const contenedorPlayer = document.createElement('span');

      function hablarConSintetizadorLocal(textoOriginal) {
        if (!('speechSynthesis' in window)) {
          btnVoz.textContent = '⚠️ Navegador sin soporte de voz';
          btnVoz.disabled = false;
          return;
        }
        window.speechSynthesis.cancel();
        const textoLimpio = textoOriginal.replace(/\[([^\]]+)\]/g, '$1. ').replace(/[*_`#>-]+/g, ' ');
        const utter = new SpeechSynthesisUtterance(textoLimpio);
        utter.lang = 'es-ES';
        const voces = window.speechSynthesis.getVoices();
        const vozEs = voces.find(v => v.lang && v.lang.toLowerCase().startsWith('es'));
        if (vozEs) utter.voice = vozEs;
        btnVoz.textContent = '⏹️ Detener voz (Respaldo Español)';
        btnVoz.disabled = false;
        utter.onend = () => {
          btnVoz.textContent = '🔊 Escuchar respuesta';
        };
        utter.onerror = () => {
          btnVoz.textContent = '🔊 Escuchar respuesta';
        };
        window.speechSynthesis.speak(utter);
      }

      async function reproducirVoz() {
        if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel();
          btnVoz.textContent = '🔊 Escuchar respuesta (ElevenLabs)';
          return;
        }
        btnVoz.disabled = true;
        btnVoz.textContent = '⏳ Generando voz con ElevenLabs...';
        try {
          const rVoz = await fetch('/api/voz', {
            method: 'POST',
            headers: obtenerHeaders(),
            body: JSON.stringify({ texto: texto })
          });
          if (!rVoz.ok) {
            hablarConSintetizadorLocal(texto);
            return;
          }
          const blob = await rVoz.blob();
          const urlAudio = URL.createObjectURL(blob);
          contenedorPlayer.innerHTML = '';
          const audioEl = document.createElement('audio');
          audioEl.controls = true;
          audioEl.src = urlAudio;
          contenedorPlayer.appendChild(audioEl);
          btnVoz.textContent = '🔊 Volver a generar audio (ElevenLabs)';
          btnVoz.disabled = false;
          audioEl.play().catch(() => {});
        } catch (e) {
          hablarConSintetizadorLocal(texto);
        }
      }

      btnVoz.addEventListener('click', reproducirVoz);
      barraAudio.appendChild(btnVoz);
      barraAudio.appendChild(contenedorPlayer);
      div.appendChild(barraAudio);

      const autoVoz = document.getElementById('auto-voz');
      if (autoVoz && autoVoz.checked) {
        reproducirVoz();
      }
    }

    mensajes.appendChild(div);
    mensajes.scrollTop = mensajes.scrollHeight;
  }

  document.getElementById('btn-conectar').addEventListener('click', async () => {
    const ok = await cargarAgentes(false);
    if (!ok) {
      agregarMensaje('Intento de acceso rechazado por el servidor (HTTP 401). Verifica tu TOKEN_ACCESO.', 'agent error', '<span>Seguridad FastAPI</span>');
    } else {
      agregarMensaje('Acceso autorizado correctamente. Catálogo A2A cargado.', 'agent', '<span class="tag-a2a">Control de acceso OK</span>');
    }
  });

  document.getElementById('btn-redescubrir').addEventListener('click', () => {
    cargarAgentes(true);
  });

  document.getElementById('btn-nueva').addEventListener('click', () => {
    contextId = null;
    mensajes.innerHTML = '';
    agregarMensaje('Nueva sesión iniciada.', 'agent');
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const texto = input.value.trim();
    agregarMensaje(texto || '(mensaje vacío)', 'user', '<span>Solicitud Usuario</span>');
    input.value = '';

    btnEnviar.disabled = true;
    btnEnviar.textContent = 'Procesando...';
    input.disabled = true;
    const quitarLoading = mostrarLoading('Consultando al Coordinador y agentes A2A... Por favor espera');

    try {
      const r = await fetch('/chat', {
        method: 'POST',
        headers: obtenerHeaders(),
        body: JSON.stringify({ mensaje: texto, context_id: contextId })
      });
      const data = await r.json();
      quitarLoading();

      if (!r.ok) {
        if (r.status === 401 || r.status === 403) {
          actualizarBadgeAcceso(false, 'Acceso rechazado (' + r.status + ')');
        }
        agregarMensaje(
          data.detail || 'Error en la solicitud',
          'agent error',
          '<span>HTTP ' + r.status + '</span>'
        );
        return;
      }

      actualizarBadgeAcceso(true, 'Acceso autorizado (200)');
      contextId = data.context_id;

      const agentes = (data.agentes_participantes || []).join(', ') || 'Coordinador';
      const estado = data.estado || 'completado';
      let clase = 'agent';
      if (estado === 'error_proveedor_o_agente') clase = 'agent error';
      if (estado === 'datos_faltantes' || estado === 'fuera_de_alcance') clase = 'agent warn';

      const meta = '<span class="tag-a2a">A2A: ' + agentes + '</span><span>Estado: ' + estado + '</span><span>Contexto: ' + (contextId ? contextId.slice(0, 8) : '-') + '</span>';
      agregarMensaje(data.respuesta, clase, meta, true);
    } catch (err) {
      quitarLoading();
      agregarMensaje('Error de comunicación con el servidor local.', 'agent error');
    } finally {
      btnEnviar.disabled = false;
      btnEnviar.textContent = 'Enviar consulta';
      input.disabled = false;
      input.focus();
    }
  });
</script>
</body>
</html>
"""
