"""Herramientas del agente de innovación.

Base de conocimiento local con metodologías, técnicas de ideación, marcos de
experimentación y guías para el Business Model Canvas / Value Proposition
Canvas. No usa internet.
"""

from __future__ import annotations

from langchain_core.tools import tool


METODOLOGIAS: list[dict] = [
    {
        "nombre": "Design Thinking",
        "enfoque": "centrado en el usuario",
        "descripcion": (
            "Metodología para resolver problemas complejos poniendo al usuario "
            "en el centro: empatizar, definir, idear, prototipar y testear."
        ),
        "cuando_usar": "Cuando se necesita entender profundamente al usuario y co-crear soluciones.",
    },
    {
        "nombre": "Lean Startup",
        "enfoque": "validación rápida",
        "descripcion": (
            "Enfoque para desarrollar productos mediante ciclos construir-medir-"
            "aprender, con MVP y métricas accionables."
        ),
        "cuando_usar": "Cuando hay incertidumbre alta y se quiere validar hipótesis con poco costo.",
    },
    {
        "nombre": "Agile / Scrum",
        "enfoque": "iterativo e incremental",
        "descripcion": (
            "Marco de trabajo iterativo con sprints, roles definidos y mejora "
            "continua basada en feedback."
        ),
        "cuando_usar": "Cuando se busca entregar valor de forma incremental y adaptarse al cambio.",
    },
    {
        "nombre": "Double Diamond",
        "enfoque": "divergencia y convergencia",
        "descripcion": (
            "Modelo de diseño en dos diamantes: descubrir, definir, desarrollar "
            "y entregar."
        ),
        "cuando_usar": "Para estructurar procesos de diseño end-to-end.",
    },
    {
        "nombre": "Jobs to be Done",
        "enfoque": "necesidades del cliente",
        "descripcion": (
            "Marco para entender qué 'trabajo' intenta resolver el cliente y "
            "por qué contrata un producto o servicio."
        ),
        "cuando_usar": "Para descubrir oportunidades de innovación basadas en necesidades reales.",
    },
]


TECNICAS: list[dict] = [
    {
        "nombre": "Crazy Eights",
        "fase": "divergencia",
        "descripcion": "Generar 8 ideas en 8 minutos, una por minuto, para forzar creatividad.",
        "cuando_usar": "Para generar muchas ideas rápidas en grupos.",
    },
    {
        "nombre": "SCAMPER",
        "fase": "divergencia",
        "descripcion": "Lista de verificación: Sustituir, Combinar, Adaptar, Modificar, Poner otro uso, Eliminar, Reordenar.",
        "cuando_usar": "Para mejorar o reinventar un producto o servicio existente.",
    },
    {
        "nombre": "Brainwriting",
        "fase": "divergencia",
        "descripcion": "Los participantes escriben ideas en silencio y las pasan para que otros las amplíen.",
        "cuando_usar": "Cuando se quiere evitar el dominio de voces fuertes en la ideación.",
    },
    {
        "nombre": "How Might We",
        "fase": "convergencia",
        "descripcion": "Convertir insights en preguntas de oportunidad para guiar la ideación.",
        "cuando_usar": "Para pasar de hallazgos a preguntas accionables.",
    },
    {
        "nombre": "Dot Voting",
        "fase": "convergencia",
        "descripcion": "Votación con puntos para priorizar ideas de forma rápida y visual.",
        "cuando_usar": "Para seleccionar ideas prometedoras en grupo.",
    },
]


MARCOS: list[dict] = [
    {
        "nombre": "A/B Testing",
        "tipo_prueba": "comparativa",
        "descripcion": "Comparar dos variantes para medir cuál performa mejor según una métrica.",
        "cuando_usar": "Cuando se tiene tráfico y se quiere optimizar una variable.",
    },
    {
        "nombre": "Smoke Test",
        "tipo_prueba": "demanda",
        "descripcion": "Lanzar una landing o anuncio para medir interés antes de construir el producto.",
        "cuando_usar": "Para validar demanda con bajo costo.",
    },
    {
        "nombre": "Concierge",
        "tipo_prueba": "servicio manual",
        "descripcion": "Entregar el servicio de forma manual y personalizada para validar valor.",
        "cuando_usar": "Para validar la propuesta de valor con clientes reales.",
    },
    {
        "nombre": "Wizard of Oz",
        "tipo_prueba": "simulación",
        "descripcion": "Simular funcionalidad automatizada con operación manual detrás de escena.",
        "cuando_usar": "Para probar la experiencia sin construir toda la tecnología.",
    },
    {
        "nombre": "MVP",
        "tipo_prueba": "producto mínimo",
        "descripcion": "Versión mínima del producto que permite aprender con clientes reales.",
        "cuando_usar": "Para validar hipótesis de solución con el menor esfuerzo.",
    },
]


BLOQUES_MODELO: list[dict] = [
    {
        "bloque": "propuesta de valor",
        "guia": "Define qué problema resuelves y qué beneficio entregas al cliente.",
        "preguntas": [
            "¿Qué problema resuelve?",
            "¿Qué beneficios entrega?",
            "¿Por qué es diferente?",
        ],
    },
    {
        "bloque": "segmentos de clientes",
        "guia": "Identifica para quién creas valor y qué necesidades tienen.",
        "preguntas": [
            "¿Quién es el cliente?",
            "¿Qué necesidades tiene?",
            "¿Qué segmentos priorizar?",
        ],
    },
    {
        "bloque": "canales",
        "guia": "Cómo llegas al cliente y entregas la propuesta de valor.",
        "preguntas": [
            "¿Cómo se entera el cliente?",
            "¿Cómo se entrega el producto?",
        ],
    },
    {
        "bloque": "relacion con clientes",
        "guia": "Tipo de relación que estableces con cada segmento.",
        "preguntas": [
            "¿Asistencia personal o automatizada?",
            "¿Comunidad o autoservicio?",
        ],
    },
    {
        "bloque": "fuentes de ingresos",
        "guia": "Cómo capturas valor económico de cada segmento.",
        "preguntas": [
            "¿Venta única o recurrente?",
            "¿Suscripción, licencia o freemium?",
        ],
    },
    {
        "bloque": "recursos clave",
        "guia": "Activos necesarios para que el modelo funcione.",
        "preguntas": [
            "¿Qué recursos físicos, intelectuales o humanos se requieren?",
        ],
    },
    {
        "bloque": "actividades clave",
        "guia": "Acciones más importantes para operar el modelo.",
        "preguntas": [
            "¿Qué debe hacer la empresa muy bien?",
        ],
    },
    {
        "bloque": "socios clave",
        "guia": "Red de proveedores y socios que optimizan el modelo.",
        "preguntas": [
            "¿Qué socios son críticos?",
            "¿Qué actividades externalizar?",
        ],
    },
    {
        "bloque": "estructura de costos",
        "guia": "Costos más importantes para operar el modelo.",
        "preguntas": [
            "¿Costos fijos o variables?",
            "¿Economías de escala?",
        ],
    },
]


def _normalizar(texto: str) -> str:
    return (texto or "").strip().lower()


@tool
def consultar_metodologias_innovacion(enfoque: str) -> list[dict]:
    """Consulta metodologías ágiles y de innovación.

    enfoque: texto a buscar (por ejemplo "usuario", "validación", "agile").
    Devuelve una lista de metodologías. Si no hay coincidencias, devuelve [].
    """
    clave = _normalizar(enfoque)
    if not clave:
        return []
    resultados: list[dict] = []
    for item in METODOLOGIAS:
        if (
            clave in _normalizar(item["nombre"])
            or clave in _normalizar(item["enfoque"])
            or clave in _normalizar(item["descripcion"])
        ):
            resultados.append(dict(item))
    return resultados


@tool
def buscar_tecnicas_ideacion(fase: str) -> list[dict]:
    """Retorna técnicas de ideación/divergencia/convergencia.

    fase: fase o texto a buscar (por ejemplo "divergencia", "convergencia").
    Devuelve una lista de técnicas. Si no hay coincidencias, devuelve [].
    """
    clave = _normalizar(fase)
    if not clave:
        return []
    resultados: list[dict] = []
    for item in TECNICAS:
        if (
            clave in _normalizar(item["nombre"])
            or clave in _normalizar(item["fase"])
            or clave in _normalizar(item["descripcion"])
        ):
            resultados.append(dict(item))
    return resultados


@tool
def obtener_marcos_experimentacion(tipo_prueba: str) -> list[dict]:
    """Devuelve frameworks de testeo y validación.

    tipo_prueba: tipo o texto a buscar (por ejemplo "demanda", "comparativa").
    Devuelve una lista de marcos. Si no hay coincidencias, devuelve [].
    """
    clave = _normalizar(tipo_prueba)
    if not clave:
        return []
    resultados: list[dict] = []
    for item in MARCOS:
        if (
            clave in _normalizar(item["nombre"])
            or clave in _normalizar(item["tipo_prueba"])
            or clave in _normalizar(item["descripcion"])
        ):
            resultados.append(dict(item))
    return resultados


@tool
def analizar_modelo_negocio(bloque: str) -> list[dict]:
    """Retorna guías de análisis para bloques del Business Model Canvas y Value Proposition Canvas.

    bloque: nombre del bloque (por ejemplo "propuesta de valor", "canales").
    Devuelve una lista con guías. Si no hay coincidencias, devuelve [].
    """
    clave = _normalizar(bloque)
    if not clave:
        return []
    resultados: list[dict] = []
    for item in BLOQUES_MODELO:
        if clave in _normalizar(item["bloque"]):
            resultados.append(dict(item))
    if not resultados:
        for item in BLOQUES_MODELO:
            if any(palabra in _normalizar(item["bloque"]) for palabra in clave.split()):
                resultados.append(dict(item))
    return resultados