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

    enfoque: texto a buscar (por ejemplo "usuario", "validación", "agile", "todas").
    Devuelve una lista de metodologías.
    """
    clave = _normalizar(enfoque)
    if not clave or clave in ("todas", "todos", "metodologias", "metodologías", "innovacion", "innovación", "catalogo"):
        return [dict(item) for item in METODOLOGIAS]
    resultados: list[dict] = []
    for item in METODOLOGIAS:
        if (
            clave in _normalizar(item["nombre"])
            or clave in _normalizar(item["enfoque"])
            or clave in _normalizar(item["descripcion"])
        ):
            resultados.append(dict(item))
    return resultados or [dict(item) for item in METODOLOGIAS]


@tool
def buscar_tecnicas_ideacion(fase: str) -> list[dict]:
    """Retorna técnicas de ideación/divergencia/convergencia.

    fase: fase o texto a buscar (por ejemplo "divergencia", "convergencia", "todas").
    Devuelve una lista de técnicas.
    """
    clave = _normalizar(fase)
    if not clave or clave in ("todas", "todos", "ideacion", "ideación", "tecnicas", "técnicas"):
        return [dict(item) for item in TECNICAS]
    resultados: list[dict] = []
    for item in TECNICAS:
        if (
            clave in _normalizar(item["nombre"])
            or clave in _normalizar(item["fase"])
            or clave in _normalizar(item["descripcion"])
        ):
            resultados.append(dict(item))
    return resultados or [dict(item) for item in TECNICAS]


@tool
def obtener_marcos_experimentacion(tipo_prueba: str) -> list[dict]:
    """Devuelve frameworks de testeo y validación.

    tipo_prueba: tipo o texto a buscar (por ejemplo "demanda", "comparativa", "todos").
    Devuelve una lista de marcos.
    """
    clave = _normalizar(tipo_prueba)
    if not clave or clave in ("todas", "todos", "experimentacion", "experimentación", "marcos", "validacion", "validación"):
        return [dict(item) for item in MARCOS]
    resultados: list[dict] = []
    for item in MARCOS:
        if (
            clave in _normalizar(item["nombre"])
            or clave in _normalizar(item["tipo_prueba"])
            or clave in _normalizar(item["descripcion"])
        ):
            resultados.append(dict(item))
    return resultados or [dict(item) for item in MARCOS]


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
    if not resultados and clave in ("todos", "todas", "modelo", "canvas", "negocio", "bmc", "catalogo"):
        return [dict(item) for item in BLOQUES_MODELO]
    return resultados


NOTICIAS_Y_TENDENCIAS: list[dict] = [
    {
        "titulo": "Auge de la IA Agéntica y Sistemas Multi-Agente (Protocolo A2A)",
        "categoria": "inteligencia artificial, agentes, tecnologia, noticias",
        "fecha_referencia": "Tendencia 2025-2026",
        "resumen": (
            "Las organizaciones están pasando de chatbots aislados a ecosistemas de agentes "
            "especializados que colaboran entre sí mediante protocolos abiertos como A2A (Agent-to-Agent), "
            "automatizando flujos complejos de investigación, operaciones y atención al cliente."
        ),
        "impacto_negocio": "Reducción de tiempos operativos en un 40-60% y mayor precisión al delegar tareas en agentes expertos.",
    },
    {
        "titulo": "Prototipado hiperrápido con IA Generativa y plataformas No-Code / Low-Code",
        "categoria": "experimentacion, mvp, startups, tendencias, desarrollo",
        "fecha_referencia": "Tendencia 2025-2026",
        "resumen": (
            "Los equipos de innovación validan hipótesis de negocio y lanzan MVPs funcionales en días "
            "en lugar de meses combinando asistentes de código por IA y herramientas No-Code."
        ),
        "impacto_negocio": "Disminución drástica del costo de experimentación (Lean Startup) y validación temprana de demanda.",
    },
    {
        "titulo": "Innovación Sostenible, Economía Circular y Cleantech",
        "categoria": "sostenibilidad, esg, economia circular, modelos de negocio, noticias",
        "fecha_referencia": "Tendencia 2025-2026",
        "resumen": (
            "El rediseño de modelos de negocio hacia cadenas de suministro circulares, trazabilidad "
            "de huella de carbono y materiales biodegradables se consolida como requisito regulatorio y de mercado."
        ),
        "impacto_negocio": "Apertura de nuevos segmentos de clientes conscientes y acceso a financiamiento verde.",
    },
    {
        "titulo": "Open Innovation y Corporate Venturing (Alianzas Corporativos-Startups)",
        "categoria": "corporativo, startups, venture client, innovacion abierta, tendencias",
        "fecha_referencia": "Tendencia 2025-2026",
        "resumen": (
            "Las grandes empresas adoptan el modelo 'Venture Client': en lugar de desarrollar todo internamente, "
            "se convierten en clientes tempranos de startups tecnológicas para integrar innovación ágilmente."
        ),
        "impacto_negocio": "Aceleración del time-to-market y transferencia tecnológica con menor riesgo financiero.",
    },
    {
        "titulo": "Gemelos Digitales (Digital Twins) para Simulación de Procesos y Productos",
        "categoria": "industria, simulacion, tecnologia, operaciones, noticias",
        "fecha_referencia": "Tendencia 2025-2026",
        "resumen": (
            "Uso de réplicas virtuales conectadas en tiempo real para simular cambios en cadenas logísticas, "
            "plantas industriales o servicios antes de implementarlos en el mundo físico."
        ),
        "impacto_negocio": "Prevención de cuellos de botella y optimización de costos operativos antes de invertir en infraestructura.",
    },
    {
        "titulo": "Hiperpersonalización centrada en Jobs-to-be-Done en tiempo real",
        "categoria": "clientes, experiencia de usuario, diseno, tendencias",
        "fecha_referencia": "Tendencia 2025-2026",
        "resumen": (
            "Las propuestas de valor dinámicas adaptan productos, precios y canales en tiempo real según "
            "el contexto y el 'trabajo por resolver' (Job to be Done) de cada usuario."
        ),
        "impacto_negocio": "Incremento en tasas de conversión y retención en modelos de suscripción y comercio digital.",
    },
]


@tool
def consultar_noticias_tendencias_innovacion(tema: str) -> list[dict]:
    """Consulta noticias recientes y tendencias actuales de innovación, tecnología y modelos de negocio.

    tema: palabra clave a buscar (por ejemplo "noticias", "tendencias", "ia",
    "agentes", "sostenibilidad", "startups", "mvp", "todas"). Devuelve una
    lista de noticias y tendencias verificadas con su resumen e impacto.
    """
    clave = _normalizar(tema)
    if not clave or clave in (
        "noticias",
        "noticia",
        "tendencias",
        "tendencia",
        "actualidad",
        "novedades",
        "innovacion",
        "innovación",
        "todas",
        "todos",
        "general",
    ):
        return [dict(item) for item in NOTICIAS_Y_TENDENCIAS]

    resultados: list[dict] = []
    palabras = [
        p for p in clave.split()
        if len(p) > 1 and p not in ("de", "la", "el", "en", "sobre", "las", "los", "que", "con", "para", "innovacion", "innovación", "noticias", "tendencias")
    ]
    for item in NOTICIAS_Y_TENDENCIAS:
        texto_busqueda = _normalizar(
            f"{item['titulo']} {item['categoria']} {item['resumen']} {item['impacto_negocio']}"
        )
        if clave in texto_busqueda or any(p in texto_busqueda for p in palabras):
            resultados.append(dict(item))

    if not resultados:
        # Si pidió algo general de tendencias/noticias que no coincidió con una palabra exacta,
        # entregamos el panorama completo de tendencias de innovación disponibles.
        return [dict(item) for item in NOTICIAS_Y_TENDENCIAS]
    return resultados